SET infile=%1
SET mypath=%~dp1
pandoc -f markdown_github %infile% --standalone --smart --self-contained --css %mypath%dark.css -t html5 -o %infile:~0,-2%html
