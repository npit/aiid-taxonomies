mkdir -p trash
echo "Moving pkl caches to trash:"
find v2/ -iname '*.pkl' 
find v2/ -iname '*.pkl' -exec mv {} trash \;
python parsexl.py v2/AIID_Technical_Taxonomies_v2.xlsx && mv annotations.json v2/annotations/
