Contents
=======
The file contains the IDs of Stations in Jyväskylä taken from the LVM.xml file. The goal is to use as a base to filter out data from JKL only.
The assumptions was made that the xml file has a newline after each station. This assimption might be wrong in general but works for now.
There are also assumptions about the order of the attributes => This method cannot be used in general!!

Creation
========

Michael Cochez : I used grep + sed to filter the IDs out.

grep "Station StationId.*city_id='179'" LVM.xml | sed "s/<Station StationId='\(.*\)' Name.*/\1/" > JyväskyläStationIDs.txt
