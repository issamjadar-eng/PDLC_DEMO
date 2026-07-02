<!--
conversion: faithful full-text conversion of the FDA "Portable Document Format
(PDF) Specifications" Technical Specifications Document, v4.1 (September 2016).
source: ../source/pdf-specifications.pdf (10 pages; fda.gov/media/76797)
method: pdftotext -layout + manual structural review; tables reconstructed
verbatim; footnote markers preserved as [n]. Verify verbatim quotes against
the byte-correct source PDF.
-->

# PORTABLE DOCUMENT FORMAT (PDF) SPECIFICATIONS

**Technical Specifications Document**

This Document is incorporated by reference into the following Guidance Document(s):

> Guidance for Industry Providing Regulatory Submissions in Electronic Format — Certain Human Pharmaceutical Product Applications and Related Submissions Using the eCTD Specifications

For questions regarding this technical specifications document, contact CDER at esub@fda.hhs.gov or CBER at esubprep@fda.hhs.gov

U.S. Department of Health and Human Services
Food and Drug Administration
Center for Drug Evaluation and Research (CDER)
Center for Biologics Evaluation and Research (CBER)

September 2016
v4.1

## Revision History

| Date | Version | Summary of Revisions |
|------|---------|----------------------|
| 2005-04-08 | 1.0 | Initial version |
| 2008-06-04 | 2.0 | Changed "Bookmarks and Page" to "Bookmarks Panel and Page" in Open Dialog Box section |
| 2011-12-20 | 3.0 | Updated to align with ICH recommendation on PDF version 1.7; add "Purpose" section; clarify specifications related to security, usability, and promotional materials; revise list of standard fonts; add PDF optimization; and incorporate editorial changes |
| 2012-1-13 | 3.1 | Clarified language on acceptable PDF versions for documents; added page numbers |
| 2014-9-26 | 4.0 | Updated to align with ICH recommendation on PDF/A; clarify embedding of fonts and font size in embedded images; revise specifications related to document naviagation; and indicate maximum allowable PDF file size |
| 2016-9-14 | 4.1 | Updated "Special Considerations for Promotional Labeling and Advertising Material" section |

_Contains Nonbinding Recommendations_

## PURPOSE

These specifications are for creating documents in Portable Document Format (PDF) for submission to CDER or CBER, that align with ICH M2 recommendations [1] and that are in a format that the receiving Center currently supports. For purposes of this document, "supports" means the receiving Center has established processes and technology infrastructure to support the receipt, processing, review and archive of files in the specified standard format. PDF is an open, published format created by Adobe Systems Incorporated (http://www.adobe.com). Software from a variety of sources can be used to create files in the PDF format.

## VERSION

PDF versions 1.4 through 1.7, PDF/A-1 and PDF/A-2 are acceptable for documents. Submitted PDF files should be readable by Adobe Acrobat X, should not require additional software or plug-ins to be read and navigated, and should be text searchable. If plug-ins are used during the creation of a PDF document, prior to submitting the document, ensure that a plug-in is not needed for review or archive.

PDF files must not contain JavaScript; dynamic content which can include audio, video or special effects and animations; attachments or 3D content. [2] Do not include PDF annotations in documents. [3] Ensure that all hypertext links in documents remain active after conversion to PDF/A.

## SECURITY

Do not activate security settings or password protection. The integrity of the submitted files is maintained through Agency security and archival processes. A copy of the files, generated from the submitted files, will be provided to the reviewer. The reviewer should be able to print, select text and graphics, and make changes to text, notes and form fields using the provided copy.

FDA Forms downloaded from the FDA Forms website contain security settings that prevent changing the documents. These forms should be submitted as provided, with no additional security added and without removing the provided security settings.

## FONTS

Fully embed all non-standard fonts. PDF viewing software automatically substitutes a font to display text if the font used to create the text is unavailable on the reviewer's computer. In some cases, font substitution can occur even when the fonts are available. For example, Helvetica or Times are substituted even if available on the reviewer's computer. Font substitution can affect a document's appearance and structure, and in some cases it can affect the information conveyed by a document.

Font availability to the reviewer is ensured if all non-standard fonts are fully embedded. When fonts are embedded, all characters for the font should be included not just a subset of the fonts being used in the document. Inspect documents to make sure all non-standard fonts are fully embedded prior to submission.

Font embedding does not always solve the problems that occur when a reviewer tries to copy and paste text from a PDF document into another software format. If the font is not available on the reviewer's computer, font substitution results, even if the fonts are embedded. This problem is avoided if the fonts are restricted to the standard fonts listed in Table 1.

**Table 1: List of Standard Fonts**

| Font type | Font name |
|-----------|-----------|
| Serif | Times New Roman; Times New Roman Italic; Times New Roman Bold; Times New Roman Bold Italic |
| Sans Serif | Arial; Arial Italic; Arial Bold; Arial Bold Italic |
| Non Proportional | Courier New; Courier New Italic; Courier New Bold; Courier New Bold Italic |
| Other | Symbol; Zapf Dingbats |

Use font sizes ranging from 9 to 12 point. [4] Times New Roman 12-point font is recommended for narrative text. When choosing a point size for tables, a balance should be made between providing sufficient information on a single page that may facilitate data comparisons while still achieving a point size that remains legible. Generally, point sizes 9-10 are recommended for tables; smaller point sizes should be avoided. Ten point fonts are recommended for footnotes.

When creating documents which include scanned images, ensure that any resizing of the image does not reduce the effective font size below the recommended size.

Black is the recommended font color [5] except that blue can be used for hypertext links. Light colors do not print well on grayscale printers. Any colors used should be tested prior to submission by printing sample pages from the document using a grayscale printer.

## PAGE ORIENTATION

Save the page orientation for proper viewing and printing within the document. Proper page orientation eliminates the need for reviewers to rotate pages. For example, setting page orientation of landscape pages to landscape prior to saving the PDF document in final form ensures a correct page presentation.

## PAGE SIZE AND MARGINS

Set up the print area for pages to fit on a sheet of paper that is 8.5 inches by 11 inches. A margin of at least 3/4 of an inch on the left side of page avoids obscuring information when pages are subsequently printed and bound. Setting the margin for at least 3/8 of an inch on the other sides is sufficient. For pages in landscape orientation, a margin of 3/4 of an inch at the top allows more information to be displayed legibly on the page. Header and footer information should not invade the specified margins (i.e., header and footer information should not appear within 3/8 of an inch of the edge of the 8.5 by 11 inch page), so the text will not be lost upon printing or being bound. These margins allow printing on A4 as well. Oversized documents (e.g., CAD drawings or other specialized documents) and promotional materials submitted in PDF format should be created according to their actual page size.

## SOURCE OF ELECTRONIC DOCUMENTS

Avoid image-based PDF files whenever possible. PDF documents produced by scanning paper documents usually have poorer image resolution than PDF documents produced from electronic source documents such as word processing files. Scanned documents are generally more difficult to read and do not allow the reviewer to search or copy and paste text for editing in other documents. If scanned files must be submitted, they should be made text searchable where possible. If optical character recognition software is used, verify that imaged text is converted completely and accurately.

## METHODS FOR CREATING PDF DOCUMENTS AND IMAGES

Use the dpi settings in Table 2 for scanning documents. Scanned documents scanned at a resolution of 300 dots per inch (dpi) ensure that the pages of the document are legible both on the computer screen and when printed and, at the same time, minimizes the file size. The use of grayscale and color significantly increases the file size and should be used only when these features improve the reviewability of the material. After scanning, avoid resampling to a lower resolution. A captured image should not be subjected to non-uniform scaling (i.e., sizing). See the following table for resolutions for various images.

**Table 2: Scanning Resolution**

| Document type | Resolution |
|---------------|------------|
| Handwritten notes | 300 dpi (black ink) |
| Plotter output graphics | 300 dpi |
| Photographs – black and white | 600 dpi (8 bit gray scale) |
| Photographs – color | 600 dpi (24 bit RGB) |
| Gels and karyotypes | 600 dpi (8 bit grayscale depth) |
| High pressure liquid chromatography | 300 dpi |

## IMAGE COMPRESSION TO REDUCE FILE SIZE

Compress files using either Zip/Flate or CCITT Group 4. File compression is a method for reducing file size. Some methods of compression can result in loss of data and can introduce compression artifacts that affect the reviewability of the information. The following two methods provide lossless compression.

- Zip/Flate (one technique with two names) for lossless compression of color and grayscale images is specified in Internet RFC 1950 and RFC 1951.
- CCITT Group 4 Fax compression technique recommendations for lossless compression of black and white images is specified in T.6 (1988) - Facsimile coding schemes and coding control functions for Group 4 facsimile apparatus.

## OPTIMIZE FOR FAST WEB VIEW

Create files from source documents using the "Optimize the PDF for fast web view" option to reduce file sizes and file opening times.

## IMAGE COLOR MATCHING

Because color varies from monitor to monitor, it is difficult to ensure that the reviewer will see exactly the same color as in the actual image. However, for printing, there is more control over the color by using CMYK (Cyan, Magenta, Yellow, Black) color model as opposed to the RGB model. Pantone Matching using the color profile provided by CMYK ensure color consistency for printing. The International Color Consortium (ICC) [6] color profile specification is used when PDF documents are printed.

## USE OF THUMBNAILS

PDF documents do not need embedded thumbnails.

## DOCUMENT NAVIGATION

A table of contents (TOC), hypertext links and bookmarks provide essential navigation through PDF documents. Include a hypertext linked TOC and bookmarks in documents 5 pages or longer. Use hypertext links throughout the body of all documents to link to supporting annotations, related sections, references, appendices, tables or figures that are not located on the same page as the narrative text. Hypertext links in text can be designated by rectangles using thin lines or by blue text. A consistent method of designating links in a document avoids confusion. Hypertext links that open a file or document should be set to open the file or document in a new window. Using relative paths when creating hypertext links minimizes the loss of hyperlink functionality when submissions are loaded onto network servers; both absolute links that reference specific drives and links to root directories do not work once the submission is loaded.

The document TOC helps the reviewer navigate to the information of interest within the document that is not provided in the submission table of contents. For documents with a table of contents, provide bookmarks and hypertext links for each item listed in the table of contents including all tables, figures, publications, other references, and appendices that are essential for navigation through documents. The use of invisible rectangles and blue text in the table of contents for hypertext links avoids obscuring text. Other help for navigation includes a bookmark hierarchy identical to the table of contents; up to four levels deep in the hierarchy.

When creating bookmarks and hyperlinks, set the magnification setting to "Inherit Zoom" so the destination page displays at the same magnification level used in the primary document.

## INITIAL VIEW SETTINGS

Set the Navigation Tab to open to "Bookmarks Panel and Page." This sets the initial document view when the file is opened. If there are no bookmarks, set the Navigation Tab to "Page Only." Page Layout and Magnification should be set to "Default."

## PAGE NUMBERING

In general, it is easier to navigate through an electronic document if the page numbers for the document and the PDF file are the same, with the initial page of the document numbered as page one. There is an exception when a document is split because of its size and the second or subsequent file is numbered consecutively to that of the first or preceding file.

## NAMING PDF FILES

Use lower case characters and avoid using special characters except hyphens and underscores in file names. Special characters to avoid include punctuation, spaces, or other non-alphanumeric symbols. The current FDA validation criteria and the ICH eCTD specification both provide additional guidance on allowable special characters in file names.

## SPECIAL CONSIDERATIONS FOR PROMOTIONAL LABELING AND ADVERTISING MATERIAL

Promotional materials submitted in PDF format may need special consideration to ensure accurate representation of the actual image. PDF restrictions for font size, color, and annotations stated in this document are not applicable to these materials. Since color varies from monitor to monitor, it is difficult to ensure that the reviewer will see exactly the same color as in the actual image. Provide images at the highest resolution and depth practical. For photographs, the image should be obtained with a resolution of at least 600 dpi. Documents that are available only in paper should be scanned at resolutions that will ensure the pages are legible both on the computer monitor and when printed; at least 600 dpi is recommended. Promotional material should be submitted according to its actual size when practical. When an image size is altered, the original dimensions must be stated. Images of three-dimensional promotional pieces must show all sides and components.

Promotional materials submitted in PDF format may need special consideration to ensure accurate representation of functionality. For example, screenshots of websites submitted in PDF format should contain links that allow the reviewer to click on them to simulate navigation in the actual website. Dynamic content such as audio, video, special effects, animations, attachments or 3D content are permitted if embedded in the PDF and playable via Adobe Acrobat X without the need for plug-ins or other special software.

---

Footnotes:

[1] ICH has recommended several file formats for the exchange of regulatory documents. See http://estri.ich.org/recommendations/index.htm
[2],[3] Exception noted in "Special Considerations for Promotional Labeling and Advertising Material"
[4],[5] Exception noted in "Special Considerations for Promotional Labeling and Advertising Material"
[6] http://www.color.org/
