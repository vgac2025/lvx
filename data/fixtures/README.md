# Livre de test — Wailly, Le Roi de l'inconnu

Place the PDF file here:

```
data/fixtures/wailly_le_roi_de_l_inconnu.pdf
```

Or set environment variable:

```
ARTCB_TEST_BOOK_PDF=/home/lvx/Downloads/wailly_le_roi_de_l_inconnu.pdf
```

Then run:

```bash
python3 -m pytest tests/test_book_wailly.py -v
```

**Note:** The PDF is NOT committed to git (copyright). Each developer copies it locally.
