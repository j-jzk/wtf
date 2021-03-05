#!/bin/sh
echo "Compiling"
python3 src/compiler.py < test.wtf > test.bf 

echo "Executing"
beef test.bf
