# ECO-PATH Pathway Activity Explorer

This folder contains the public, standalone version of the ECO-PATH pathway activity explorer.

## Files

- `index.html`: self-contained interactive pathway explorer.
- `.nojekyll`: tells GitHub Pages to serve the site without Jekyll processing.

## Recommended publication route

Create a separate public GitHub repository for this folder, for example:

```text
ecopath-pathway-explorer
```

Upload only the contents of this `public_site/` folder to that repository. Do not upload the full ECO-PATH working directory unless every file has been checked for publication suitability.

## GitHub Pages settings

After uploading the files:

1. Open the repository on GitHub.
2. Go to `Settings`.
3. Go to `Pages`.
4. Under `Build and deployment`, choose `Deploy from a branch`.
5. Select branch `main` and folder `/root`.
6. Save.

The public page will usually become available at:

```text
https://<github-username>.github.io/ecopath-pathway-explorer/
```

## Command-line upload option

If Git is available and the GitHub repository already exists:

```bash
cd public_site
git init
git add index.html .nojekyll README.md
git commit -m "Publish ECO-PATH pathway activity explorer"
git branch -M main
git remote add origin https://github.com/<github-username>/ecopath-pathway-explorer.git
git push -u origin main
```

Replace `<github-username>` with the GitHub account or organization name.
