<?php

//	Test the php and C versions of getdiskusage by seeing if they produce identical output.
//	Also tests for JSON correctness, required to do a json_decode.
//	Unicode correctness was tested through manual inspection using a directory with unicode file and directory names.

function itemcmp($a, $b) {
	if ($a->path > $b->path) return 1;
	else if ($a->path < $b->path) return -1;
	return 0;
}


$path = $argv[1];
$list1 = json_decode(shell_exec("getdiskusage {$path}"))->files;
$list2 = json_decode(shell_exec("php getdiskusage.php {$path}"))->files;
if (count($list1) != count($list2)) { echo "Count is different"; exit(1); }
usort($list1, "itemcmp");
usort($list2, "itemcmp");
for ($i = 0; $i < count($list1); $i++) {
	if ($list1[$i]->path != $list2[$i]->path) { echo "Path is different on item {$i}"; exit(1); }
	if ($list1[$i]->directory != $list2[$i]->directory) { echo "Directory flag is different on item {$i}"; exit(1); }
	if ($list1[$i]->size != $list2[$i]->size) { echo "Size is different on item {$i}"; exit(1); }
}
echo "Test succeeded.\n";

?>