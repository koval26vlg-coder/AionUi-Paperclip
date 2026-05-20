import { existsSync } from 'node:fs'
import { spawn } from 'node:child_process'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

const appDir = dirname(fileURLToPath(import.meta.url))
const workspaceRoot = resolve(appDir, '..', '..')
const smlDashboardScript = resolve(appDir, 'scripts', 'export-sml-dashboard.py')
const bundledPython = resolve(workspaceRoot, '.venv-sml', 'Scripts', 'python.exe')
const pythonExecutable = process.env.PYTHON || (existsSync(bundledPython) ? bundledPython : 'python')

function smlDashboardApi(): Plugin {
  return {
    name: 'sml-dashboard-api',
    configureServer(server) {
      server.middlewares.use('/api/sml-dashboard', (_req, res) => {
        const child = spawn(pythonExecutable, [smlDashboardScript, '--json'], {
          cwd: appDir,
          windowsHide: true,
        })
        let stdout = ''
        let stderr = ''
        const timeout = setTimeout(() => {
          child.kill()
        }, 10_000)

        child.stdout.setEncoding('utf8')
        child.stderr.setEncoding('utf8')
        child.stdout.on('data', (chunk) => {
          stdout += chunk
        })
        child.stderr.on('data', (chunk) => {
          stderr += chunk
        })
        child.on('close', (code) => {
          clearTimeout(timeout)
          res.setHeader('Content-Type', 'application/json; charset=utf-8')
          if (code === 0 && stdout.trim()) {
            res.statusCode = 200
            res.end(stdout)
            return
          }
          res.statusCode = 500
          res.end(
            JSON.stringify({
              generatedAt: new Date().toISOString(),
              status: {
                state: 'error',
                label: 'Ошибка SML API',
                message: stderr || `export-sml-dashboard.py exited with code ${code}`,
              },
              totals: {
                recordsTotal: 0,
                currentRecords: 0,
                supersededRecords: 0,
                authorsTotal: 0,
                sourceFilesTotal: 0,
              },
              records: [],
              typeCounts: [],
              dailyActivity: [],
              agents: [],
            }),
          )
        })
      })
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), smlDashboardApi()],
})
