Place manually downloaded land-price source files here.

Supported formats:

- `.csv`
- `.tsv`
- `.zip` containing `.csv` or `.tsv`

Expected columns can vary. The loader looks for aliases such as:

- PNU: `PNU`, `필지고유번호`, `법정동코드`
- Land price: `공시지가`, `지가`, `LANDPRICE`

Recommended source workflow:

1. Download parcel land-price files from the official public-data or VWorld distribution pages.
2. Keep the original files unchanged when possible.
3. Drop the files into this folder.
4. Restart the server or re-run the tool.
