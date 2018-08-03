<?php
//	GetDiskUsage.php
$eol = PHP_EOL;
function putfiles($path, $depth) {
	global $eol;  $totalSize = 0;
	if ($handle = opendir($path)) {		// open the directory
		while (false !== ($entry = readdir($handle))) {
			$wholePath = $path . DIRECTORY_SEPARATOR . $entry;
			if ($entry == "." || $entry == "..") { continue; }	// skip parent/current directories  
			else if (is_dir($wholePath)) {	// if it's a subdir, recursively add files to the output
				$subdirSize = putfiles($wholePath, $depth+1);
				if ($subdirSize == -1) { closedir($handle); return -1; }
				echo "  " . json_encode((object)array('directory'=> true, 'path'=> $wholePath, 'size'=> $subdirSize), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
				$totalSize += $subdirSize;
			} else {		// if it's a file, just add the one file
				$fileSize = filesize($wholePath);
				echo "  " . json_encode((object)array('directory'=> false, 'path'=> $wholePath, 'size'=> $fileSize), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
				$totalSize += $fileSize;
			}
			echo ",{$eol}";		// end of line
		}
		closedir($handle); return $totalSize;		// return the size of the folder to the caller, to build up folder sizes for each folder and subfolder
	}
	else {  fwrite(STDERR,"Couldn't open path"); return -1; }
}
echo "{{$eol}  \"files\":{$eol}  [{$eol}";  $allsize = putfiles($argv[1], 1);
echo "  " . json_encode((object)array('directory'=> true, 'path'=> $argv[1], 'size'=> $allsize), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "{$eol}  ]{$eol}}{$eol}";
?>