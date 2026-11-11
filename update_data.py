
name: Daily Morning Macro Update

on:
  schedule:
    # 04:30 UTC every morning
    - cron: '30 4 * * *'
  workflow_dispatch:

jobs:
  update-macro-data:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run data fetcher
        run: |
          python update_data.py

      - name: Commit and push updated data.json
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add data.json
          git commit -m "chore: automated morning market data refresh [skip ci]" || echo "No changes to commit"
          git push
