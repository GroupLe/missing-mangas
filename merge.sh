#!/bin/bash
for file in ./*.csv; do
		cat $file >> result.csv
done