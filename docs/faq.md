# FAQ ❓

**MkDocs 404 for Usage?**  
- Ensure the file name matches the nav entry *exactly* (case-sensitive on GitHub Pages).  
- Put Markdown files in the `docs/` folder and set `nav` in `mkdocs.yml` accordingly.

**Windows cannot run `mkdocs` command?**  
- Install with `pip install mkdocs mkdocs-material` or run `python -m mkdocs serve`.

**No reports generated?**  
- Check `reports/` directory exists and `--report_name` is set.  
- Ensure CSV columns match the required schema.

**Strategy not recognized in CLI?**  
- Valid choices are `sma`, `momentum`, `topn_momentum`, `bbands`, `rsi`, `macd`.
