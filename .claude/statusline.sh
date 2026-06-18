#!/usr/bin/env bash
# Русская статус-строка для Claude Code.
# На вход через stdin приходит JSON с информацией о сессии.
node -e '
  let s="";
  process.stdin.on("data", d => s += d).on("end", () => {
    let j = {};
    try { j = JSON.parse(s); } catch (e) {}
    const model = (j.model && j.model.display_name) || "Claude";
    const dir = (j.workspace && j.workspace.current_dir) || j.cwd || "";
    const folder = dir.split(/[\\\/]/).filter(Boolean).pop() || dir;

    let branch = "";
    try {
      branch = require("child_process")
        .execSync("git rev-parse --abbrev-ref HEAD", { cwd: dir, stdio: ["ignore","pipe","ignore"] })
        .toString().trim();
    } catch (e) {}

    let line = "Модель: " + model + " · Папка: " + folder;
    if (branch) line += " · Ветка: " + branch;
    process.stdout.write(line);
  });
'
