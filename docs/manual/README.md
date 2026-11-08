# CMF True Stereo manual (early beta)

The PDF instruction manual. It is in early beta: still being written and checked. The **Attach manual** workflow (run by hand) uploads it to the latest
release.

- `CMF-True-Stereo-Manual.pdf`: the manual.
- `module_content.py`: its text, chapter by chapter (HTML sections).
- `build_manual.py`: builds the PDF with Playwright's Chromium, in two passes so the contents
  page shows each section's page.

Build:

    NDOT_FONT=/path/to/Ndot77JPExtended.ttf python3 build_manual.py module_content.py ../banner.png CMF-True-Stereo-Manual.pdf

Needs Playwright (Node) and poppler-utils (pdfinfo, pdftotext). Ndot 77 JP Extended is
Nothing's font and is not stored here; take it from the phone.
