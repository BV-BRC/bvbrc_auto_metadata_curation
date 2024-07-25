# bvbrc_auto_metadata_curation
Repository for the BVBRC automatic metadata curation project
Currently it has 8 different modules:

### Module 1: Metadata Curation.
This module is responsible for curating the metadata of the BVBRC genome group from Genbank and Biosample.
The metadata fields are: Host, Labhost, Collection Date, Geo Location, Isolation Source.

Input: BVBRC genome group in csv format.

Output: All extracted metadata fields in csv format.

### Module 2: Keyword Match
Given a text, this module is responsible for matching the text with a list of keywords from labhosts and isolation source.

Input: Text

Output: [Y, N] if the text contains a keyword from the labhost list and not isolation source list and similar.

### Module 3: Host Annotation
Given a text, this module queries the Host Annotation database developed by Catherine Macken and Don Dempsey.

Input: Host name Text

Output: Scientific name of the host, Common Name of the host and Score.

### Module 4: Curate Geographic Location
This module gives a curated value for geographic location or a appropriate message if the location cannot be curated by the pipeline.

Input: CSV file with the metadata fields from Module 1.

Output: CSV file with the curated geographic location.

### Module 5: Curate Collection Date
This module gives a curated value for collection date or a appropriate message if the date cannot be curated by the pipeline.

Input: CSV file with the metadata fields from Module 1.

Output: CSV file with the curated collection date and collection year.

### Module 6: Curate Host
This module gives a curated scientific name and common name for host or a appropriate message if the host cannot be curated by the pipeline.

Input: CSV file with the metadata fields from Module 1.

Output: CSV file with the curated Scientific Name and Common Name of the host.

### Module 7: Curate Labhost
This module gives a curated value for labhost or a appropriate message if the labhost cannot be curated by the pipeline.

Input: CSV file with the metadata fields from Module 1.

Output: CSV file with the curated labhost.

### Module 8: Curate Isolation Source
This module gives a curated value for isolation source or a appropriate message if the isolation source cannot be curated by the pipeline.

Input: CSV file with the metadata fields from Module 1.

Output: CSV file with the curated isolation source.
