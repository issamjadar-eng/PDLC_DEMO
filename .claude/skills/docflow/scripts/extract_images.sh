#!/bin/bash
# extract_images.sh — Extract images from source documents for docflow conversion
#
# Usage:
#   extract_images.sh <source_file> <staging_dir> <format>
#
# Arguments:
#   source_file  — Path to the source document
#   staging_dir  — Path to the staging directory (images go to staging_dir/images/)
#   format       — File format: pdf, docx, doc, xlsx
#
# Outputs images to staging_dir/images/ and prints a summary of extracted files.

set -euo pipefail

SOURCE_FILE="${1:?Usage: extract_images.sh <source_file> <staging_dir> <format>}"
STAGING_DIR="${2:?Usage: extract_images.sh <source_file> <staging_dir> <format>}"
FORMAT="${3:?Usage: extract_images.sh <source_file> <staging_dir> <format>}"

IMAGE_DIR="${STAGING_DIR}/images"
mkdir -p "${IMAGE_DIR}"

extract_pdf() {
    echo "Extracting images from PDF..."

    # Extract embedded images using pdfimages
    if command -v pdfimages &>/dev/null; then
        pdfimages -png "${SOURCE_FILE}" "${IMAGE_DIR}/extracted"

        # Count extracted images (pdfimages creates extracted-000.png, extracted-001.png, etc.)
        local count
        count=$(find "${IMAGE_DIR}" -name "extracted-*.png" -o -name "extracted-*.jpg" 2>/dev/null | wc -l | tr -d ' ')
        echo "Extracted ${count} images from PDF"
    else
        echo "WARNING: pdfimages not found. Install poppler: brew install poppler"
        exit 1
    fi
}

extract_docx() {
    echo "Extracting images from DOCX..."

    # DOCX is a ZIP file — images are in word/media/
    if unzip -l "${SOURCE_FILE}" "word/media/*" &>/dev/null; then
        unzip -o -j "${SOURCE_FILE}" "word/media/*" -d "${IMAGE_DIR}/" 2>/dev/null

        # Convert EMF/WMF to PNG if libreoffice is available
        convert_metafiles

        local count
        count=$(find "${IMAGE_DIR}" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.svg" -o -name "*.gif" \) 2>/dev/null | wc -l | tr -d ' ')
        echo "Extracted ${count} images from DOCX"
    else
        echo "No embedded images found in DOCX"
    fi
}

extract_doc() {
    echo "Extracting images from DOC (legacy format)..."

    # Convert DOC to DOCX first, then extract
    if command -v libreoffice &>/dev/null; then
        libreoffice --headless --convert-to docx --outdir "${STAGING_DIR}/" "${SOURCE_FILE}" 2>/dev/null

        # Find the converted DOCX
        local converted
        converted=$(find "${STAGING_DIR}" -name "*.docx" -maxdepth 1 | head -1)

        if [[ -n "${converted}" ]]; then
            # Extract from converted DOCX
            if unzip -l "${converted}" "word/media/*" &>/dev/null; then
                unzip -o -j "${converted}" "word/media/*" -d "${IMAGE_DIR}/" 2>/dev/null
                convert_metafiles
            fi

            local count
            count=$(find "${IMAGE_DIR}" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.svg" \) 2>/dev/null | wc -l | tr -d ' ')
            echo "Extracted ${count} images from DOC (via DOCX conversion)"
        else
            echo "WARNING: LibreOffice DOC→DOCX conversion produced no output"
        fi
    else
        echo "WARNING: libreoffice not found. Cannot extract images from DOC format."
        echo "Install: brew install --cask libreoffice"
    fi
}

extract_xlsx() {
    echo "Extracting images from XLSX..."

    # XLSX is a ZIP file — images are in xl/media/
    if unzip -l "${SOURCE_FILE}" "xl/media/*" &>/dev/null; then
        unzip -o -j "${SOURCE_FILE}" "xl/media/*" -d "${IMAGE_DIR}/" 2>/dev/null

        convert_metafiles

        local count
        count=$(find "${IMAGE_DIR}" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.svg" \) 2>/dev/null | wc -l | tr -d ' ')
        echo "Extracted ${count} images from XLSX"
    else
        echo "No embedded images found in XLSX"
    fi

    # Note: Excel charts are NOT extractable this way — they're XML definitions, not images
    echo "NOTE: Excel charts (if any) require LibreOffice render or screenshot — not auto-extractable"
}

convert_metafiles() {
    # Convert EMF/WMF files to PNG — these don't render in markdown previews
    local emf_count=0

    for metafile in "${IMAGE_DIR}"/*.emf "${IMAGE_DIR}"/*.wmf "${IMAGE_DIR}"/*.EMF "${IMAGE_DIR}"/*.WMF; do
        [[ -f "${metafile}" ]] || continue

        if command -v libreoffice &>/dev/null; then
            local basename
            basename=$(basename "${metafile%.*}")
            libreoffice --headless --convert-to png --outdir "${IMAGE_DIR}/" "${metafile}" 2>/dev/null
            rm -f "${metafile}"
            ((emf_count++))
        else
            echo "WARNING: Cannot convert ${metafile} to PNG — libreoffice not found"
        fi
    done

    if [[ ${emf_count} -gt 0 ]]; then
        echo "Converted ${emf_count} EMF/WMF files to PNG"
    fi
}

# Main
echo "=== Docflow Image Extraction ==="
echo "Source: ${SOURCE_FILE}"
echo "Format: ${FORMAT}"
echo "Output: ${IMAGE_DIR}"
echo ""

case "${FORMAT}" in
    pdf)  extract_pdf ;;
    docx) extract_docx ;;
    doc)  extract_doc ;;
    xlsx) extract_xlsx ;;
    *)
        echo "ERROR: Unsupported format '${FORMAT}'. Supported: pdf, docx, doc, xlsx"
        exit 1
        ;;
esac

echo ""
echo "=== Extraction Complete ==="

# List all extracted images
if find "${IMAGE_DIR}" -type f 2>/dev/null | grep -q .; then
    echo "Files in ${IMAGE_DIR}/:"
    find "${IMAGE_DIR}" -type f -exec basename {} \; | sort
else
    echo "No images extracted."
fi
