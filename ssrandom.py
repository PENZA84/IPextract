name: Update File and Extract IPs (IPextract Full Cycle)

on:
  workflow_dispatch:
  schedule:
    - cron: '41 2 * * *'

jobs:
  update:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout Fork
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Set up Git
        run: |
          git config --global user.name 'github-actions[bot]'
          git config --global user.email 'github-actions[bot]@users.noreply.github.com'

      - name: ПОДГОТОВКА (Создание структуры и заглушек)
        run: |
          # Создаем папки из твоего скриншота 855
          mkdir -p split splitorg archive archiveorg splitbytype
          
          # Создаем файлы-заглушки в корне
          touch proxies.txt ss.txt unique_add.txt new_proxies.txt nodup_proxies.txt
          
          # Создаем важную заглушку в папке, которую ждет ssrandom.py
          touch splitbytype/ss.txt

      - name: СБОР (Fetch из твоих источников)
        run: |
          > proxies.txt
          urls=(
            "https://raw.githubusercontent.com/Surfboardv2ray/TGParse/main/configtg.txt"
            "https://raw.githubusercontent.com/coldwater-10/Vpnclashfa/main/raw/irc.txt"
            "https://raw.githubusercontent.com/coldwater-10/Vpnclashfa/main/raw/mci.txt"
            "https://raw.githubusercontent.com/coldwater-10/Vpnclashfa/main/raw/mkb.txt"
            "https://raw.githubusercontent.com/coldwater-10/Vpnclashfa/main/raw/hy2.txt"
            "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/xray/normal/mix"
            "https://raw.githubusercontent.com/yebekhe/V2Hub/main/merged"
            "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/base64/vmess"
            "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/base64/vless"
            "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/mix"
            "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/donated"
            "https://raw.githubusercontent.com/itsyebekhe/HiN-VPN/main/subscription/normal/mix"
          )
          for url in "${urls[@]}"; do
            content=$(curl -sL "$url")
            if [ -n "$content" ]; then
              if [[ "$content" =~ ^[A-Za-z0-9+/]*={0,2}$ ]]; then
                echo "$content" | base64 -d >> proxies.txt 2>/dev/null || echo "$content" >> proxies.txt
              else
                echo "$content" >> proxies.txt
              fi
              echo "" >> proxies.txt
            fi
          done

      - name:  ЗАПУСК ПАРСЕРОВ (Processing)
        run: |
          # Последовательный запуск твоих скриптов
          python no_dup.py || echo "skip"
          python extract_ips.py || echo "skip"
          python replace_ips.py || echo "skip"
          python splitbytype.py || echo "skip"
          
          # Твой ssrandom.py теперь найдет splitbytype/ss.txt
          python ssrandom.py || echo "⚠️ ssrandom пропущен, но завод идет дальше"
          
          python split_file.py || echo "skip"
          python splitorg_file.py || echo "skip"

      - name: ОПТИМИЗАЦИЯ И ПУШ (Финальный штрих)
        run: |
          # Наш фирменный «Хирург» для Трона: режем всё, что выше 90 МБ
          python -c "
          import os
          for root, dirs, files in os.walk('.'):
              for f in files:
                  if f.endswith('.txt'):
                      p = os.path.join(root, f)
                      if os.path.getsize(p) > 90*1024*1024:
                          with open(p, 'r', encoding='utf-8') as file: lines = file.readlines()
                          with open(p, 'w', encoding='utf-8') as file: file.writelines(lines[:350000])
          "
          
          # Добавляем всё: файлы и структуру папок
          git add *.txt
          git add split/ splitorg/ archive/ archiveorg/ splitbytype/
          
          if ! git diff --cached --quiet; then
            git commit -m " Завод IPextract: база обновлена, пути исправлены 💋🍀"
            git push
          else
            echo "Ничего нового, ждем следующего цикла."
          fi
