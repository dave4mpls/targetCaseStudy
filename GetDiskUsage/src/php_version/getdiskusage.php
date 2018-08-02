<?php
//	GetDiskUsage.php
//	Case Study for Dave White
//	Candidate for Guest Reliability Engineer
//	Completed 8/2/2018

//	The fancy getdiskusage in multiplatform C is not what I would do in real life,
//	at least not for a simple script.  I would use Python or Perl or PHP, like so.

$eol = PHP_EOL;

function putfiles($path, $depth) {
	global $eol;
	$totalSize = 0;
	$skipComma = false;
	if ($handle = opendir($path)) {
		$entry = readdir($handle);
		while ($entry) {
			$skipComma = false;
			$wholePath = $path . DIRECTORY_SEPARATOR . $entry;
			if ($entry == "." || $entry == "..") {
				$skipComma = true;
			}
			else if (is_dir($wholePath)) {
				$subdirSize = putfiles($wholePath, $depth+1);
				if ($subdirSize == -1) { closedir($handle); return -1; }
				echo "  " . json_encode((object)array('directory'=> true, 'path'=> $wholePath, 'size'=> $subdirSize), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
				$totalSize += $subdirSize;
			}
			else {
				$fileSize = filesize($wholePath);
				echo "  " . json_encode((object)array('directory'=> false, 'path'=> $wholePath, 'size'=> $fileSize), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
				$totalSize += $fileSize;
			}
			$entry = readdir($handle);
			if (($entry || $depth > 0) && !$skipComma) echo ",{$eol}";
			else if (!$skipComma) echo "{$eol}";
		}
		closedir($handle);
		return $totalSize;
	}
	else {
		fwrite(STDERR,"Couldn't open path");
		return -1;
	}
}

if ($argc < 2) {
	echo "Parameter expected{$eol}";
	echo "Usage: getdiskusage path{$eol}";
	return 1;
}
echo "{{$eol}  \"files\":{$eol}  [{$eol}";
$allsize = putfiles($argv[1], 1);
echo "  " . json_encode((object)array('directory'=> true, 'path'=> $argv[1], 'size'=> $allsize), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "{$eol}";
echo "  ]{$eol}}{$eol}";
?>