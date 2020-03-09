# Date: Mar 2, 2020
# Author: Ishaat Chowdhury
# Contents: Generate call graphs for reports
#!/bin/bash
set -Eeuo pipefail

for dir in */
do
    dirname=${dir%*/}
    pyan $(find $dir -path ./tests -prune -o -name "*.py" -print) --dot --colored --no-defines --grouped | dot -Tpng -Granksep=1.5 -o $dir/$dirname.png
done
