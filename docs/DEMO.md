# PhxPict Demo Guide

## Demo readiness

PhxPict is suitable for a controlled MVP demonstration on macOS, Windows, or
Linux. It keeps photographs and the search catalog local. It is not yet a
signed consumer installer.

## Prepare on a Mac before the visit

1. Clone or download the private `BStofftTX/PhxPict` repository.
2. From Terminal in the project folder, run:

   ```bash
   chmod +x scripts/setup_macos.command
   ./scripts/setup_macos.command
   ```

3. Allow the model download to finish. This requires internet access only for
   software/model installation; photographs are not uploaded.
4. Connect the photo drive or copy a representative folder locally.
5. In PhxPict, choose **Index photo folder**. For thousands of photos, start
   this before the meeting or use a 100-300 photo subset for the live indexing
portion.

## Apple Photos and Android/Google Photos

For tomorrow's demonstration, do not index or modify the live Apple Photos
Library package. In Apple Photos on the Mac:

1. Select 100-300 representative photos.
2. Choose **File > Export > Export Unmodified Original**.
3. Export into a new ordinary folder such as `PhxPict Demo Photos`.
4. Point PhxPict at that exported folder.

If the Android phone uses Google Photos, only items that also exist as ordinary
files on the Mac can be indexed. Cloud-only Google Photos items must first be
downloaded or exported. PhxPict does not yet connect to Google Photos accounts.

After the controlled demo, a read-only Apple Photos importer and an optional
Google Photos import workflow can be evaluated separately.

After setup, future launches can use `scripts/launch_macos.command`.

On the development Apple Silicon Mac, sustained local visual tagging measured
about 0.42 seconds per image after model startup. That is roughly seven minutes
per 1,000 images or seventy minutes per 10,000 images. Hardware, image size,
format, storage speed, and model caching can change those numbers materially.

## Suggested five-minute demonstration

1. Explain that the application indexes locally and does not upload photos.
2. Show the indexed-photo total.
3. Search a broad category: `people`, `nature`, `buildings`, `automobiles`,
   `trains`, `planes`, or `warfare`.
4. Filter by capture date, then modification date.
5. Double-click a result to open the original photo.
6. Use **Next** and **Previous** to show that large result sets are paginated.

## Important boundaries to state

- Content search uses broad whole-image categories and may misclassify images.
- `people` finds photos containing people; it does not identify a named person.
- PhxPict does not yet detect objects with bounding boxes.
- Metadata indexing is quick. Local CLIP analysis is private but may take a
  long time over thousands of images, especially on CPU-only computers.
- HEIC/HEIF is supported after normal package installation. RAW camera formats
  are not yet supported.
- Use copies or read-only access for an important collection during an MVP demo.

## Fast fallback if visual setup is unavailable

The application can still index dates, file metadata, filenames, and folder
names. Run:

```bash
phxpict-cli index /path/to/photos --content-provider filename
phxpict
```

This mode is fast but content categories come only from folder and filename
words, not image pixels.
