//
//	GetDiskUsage.c
//	Case Study for Dave White
//	Candidate for Guest Reliability Engineer
//	Completed 8/2/2018
//
//	Handles Unicode filenames: tinydir library uses wide characters in Windows,
//	which we convert to UTF8.  Linux stays in UTF8 the whole time.
//

#define TRUE 1
#define FALSE 0

//	Visual Studio defines 
#define _CRT_SECURE_NO_WARNINGS

#include<stdio.h>
#include<string.h>
#include<malloc.h>
#include<sys/stat.h>
#include "tinydir.h"
#ifdef _WIN32
#else 
#include<locale.h>
#endif

char *escapeName(char *name) {
	// escapes the name's quote marks so it works in JSON; returns as new malloc'd string
	int newSize = 0;
	char *o = name;
	while (*o) {
		if (*o == '\"') newSize += 2;
		else if (*o == '\\') newSize += 2;
		else newSize++;
		o++;
	}
	char *newName = malloc((newSize + 2) * sizeof(char));
	o = name;
	char *p = newName;
	while (*o) {
		if (*o == '\"') { *p = '\\'; p++; *p = '\"'; p++; }
		else if (*o == '\\') { *p = '\\'; p++; *p = '\\'; p++; }
		else { *p = *o; p++; }
		o++;
	}
	*p = 0;
	return newName;
}

char *dirSep() {
	// Returns the OS-specific directory separator
#ifdef _WIN32
	return ("\\");
#else
	return ("/");
#endif
}

char *jsonDirSep() {
	// Returns the OS-specific directory separator escaped for JSON
#ifdef _WIN32
	return ("\\\\");
#else
	return ("/");
#endif
}


char *lineEnd() {
	// Returns OS-specific line ending.  Actually, stdout handles that, so just
	// return \n.
	return ("\n");
}

#ifdef _WIN32
wchar_t *toWideChar(char *s) {
	// Windows: allocates space and converts a regular string (UTF8) to
	// a Wide string for use with the libraries.
	UINT reqsize = MultiByteToWideChar(CP_UTF8, 0, s, -1, NULL, 0);
	if (!reqsize) { return NULL; }
	wchar_t *wideUnicodeBuffer = malloc(sizeof(wchar_t)*(4 + reqsize));
	UINT mbresult = MultiByteToWideChar(CP_UTF8, 0, s, -1, wideUnicodeBuffer, reqsize);
	if (!mbresult) { free(wideUnicodeBuffer); return NULL; }
	return wideUnicodeBuffer;
}

char *fromWideChar(wchar_t *w) {
	// Windows: allocates space and converts a wide string to a UTF8 string.
	size_t allocsize = _tcslen(w) * 4;
	char *utf8textbuffer = malloc(sizeof(char) * allocsize);  // memory is cheap -- assume every wide character becomes 4 bytes in UTF8
	UINT result2 = WideCharToMultiByte(CP_UTF8, 0, w, -1, utf8textbuffer, allocsize, NULL, NULL);
	if (!result2) {
		free(utf8textbuffer); return NULL;
	}
	return utf8textbuffer;
}
#endif

long long getFileSize(char *pathName, char *fileName) {
	long long resultSize;
	char *fullName = malloc(sizeof(char) * (strlen(pathName) + 3 + strlen(fileName)));
	strcpy(fullName, pathName);
	strcat(fullName, dirSep());
	strcat(fullName, fileName);
#ifdef _WIN32
	// Windows: convert name from UTF8 to wide characters, open, get size
	wchar_t *wideUnicodeBuffer = toWideChar(fullName);
	if (!wideUnicodeBuffer) { free(fullName); return -1; }
	HANDLE hFile = CreateFileW(wideUnicodeBuffer, GENERIC_READ,
		FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_EXISTING,
		FILE_ATTRIBUTE_NORMAL, NULL);
	free(wideUnicodeBuffer);
	if (hFile == INVALID_HANDLE_VALUE) {
		free(fullName);
		return -1; // error condition, could call GetLastError to find out more
	}
	LARGE_INTEGER size;
	if (!GetFileSizeEx(hFile, &size))
	{
		CloseHandle(hFile);
		free(fullName);
		return -1; // error condition, could call GetLastError to find out more
	}
	CloseHandle(hFile);
	resultSize = (long long)size.QuadPart;
#else
	struct stat st;
	if (stat(fullName, &st) != 0)
	{
		free(fullName); return -1;
	}
	free(fullName);
	resultSize = st.st_size;
#endif
	return resultSize;
}

long long putFiles(char *pathName, int depth) {
	// Puts the files in the given path out to stdout
	// in JSON format, and returns total directory and subdirectory size on success or -1 on error.  
	// On error, it prints the error to standard error before it returns.
	tinydir_dir dir;
	char *escapedPath;
	long long totalSize = 0;
	int skipComma = FALSE;
	escapedPath = escapeName(pathName);
#ifdef WIN32
	wchar_t * widePathName = toWideChar(pathName);
	if (!widePathName) { free(escapedPath); return -1; }
	if (tinydir_open(&dir, widePathName) == -1) { free(widePathName);  perror("Error opening directory"); goto bail; }
	free(widePathName);
#else
	if (tinydir_open(&dir, pathName) == -1) { perror("Error opening directory"); goto bail; }
#endif
	while (dir.has_next) {
		// main file reading loop
		skipComma = FALSE;
		tinydir_file file;
		if (tinydir_readfile(&dir, &file) == -1) { perror("Error reading directory"); goto bail; }
#ifdef _WIN32
		char *fileName = fromWideChar(file.name);
#else
		char *fileName = malloc(sizeof(char)*(1 + strlen(file.name)));
		strcpy(fileName, file.name);
#endif
		if (strcmp(fileName, (".")) == 0) {
			skipComma = TRUE;
		}
		else if (strcmp(fileName, ("..")) == 0) {
			skipComma = TRUE;
		}
		else if (file.is_dir) {
			// another directory: recurse to find more files
			char *newPath = (char *)malloc((strlen(pathName) + strlen(fileName) + 3) * sizeof(char));
			strcpy(newPath, pathName);
			strcat(newPath, dirSep());
			strcat(newPath, fileName);
			long long subdirSize = putFiles(newPath, depth + 1);
			free(newPath);
			if (subdirSize == -1) {
				free(fileName);
				goto bail;
			}
			// print out the directory after all its files, with total size.
			// add size to the total for this directory we are in
			char *escapedName;
			escapedName = escapeName(fileName);
			printf(("  {\"directory\":true,\"path\":\"%s%s%s\",\"size\":%lld}"), escapedPath, jsonDirSep(), escapedName, subdirSize);
			totalSize += subdirSize;
			free(escapedName);
		}
		else {
			// a file: print out its information; escape any quote marks in filenames
			char *escapedName;
			escapedName = escapeName(fileName);
			long long filesize = getFileSize(pathName, fileName);
			printf(("  {\"directory\":false,\"path\":\"%s%s%s\",\"size\":%lld}"), escapedPath, jsonDirSep(), escapedName, filesize);
			totalSize += filesize;
			free(escapedName);
		}
		free(fileName);
		// go to next file
		if (tinydir_next(&dir) == -1) { perror("Error reading next file in directory"); goto bail; }
		if ((dir.has_next || depth > 0) && !skipComma) 	//  except on very last line of topmost depth, we print a comma
			printf((",%s"), lineEnd());
		else if (!skipComma)
			printf(("%s"), lineEnd());
	}

	free(escapedPath);
	tinydir_close(&dir);
	return totalSize;

bail:
	free(escapedPath);
	tinydir_close(&dir);
	return -1;
}

int main(int argc, char *argv[])
{
#ifdef _WIN32
//	SetConsoleOutputCP(CP_UTF8);
#else
	setlocale(LC_ALL, "");
#endif
	char *helpText = ("Usage: getdiskusage path");
	if (argc < 2) {
		fprintf(stderr, ("Parameter expected%s%s%s"), lineEnd(), helpText, lineEnd());
		return 1;
	}
	else if (strcmp(argv[1], ("/?")) == 0 || strcmp(argv[1], ("--help")) == 0 || strcmp(argv[1], ("/h")) == 0 || strcmp(argv[1], ("-h")) == 0 || strcmp(argv[1], ("-H")) == 0 || strcmp(argv[1], ("/H")) == 0) {
		printf(("%s%s"), helpText, lineEnd());
		return 0;
	}
	else {
		printf(("{%s"), lineEnd());
		printf(("  \"files\":%s"), lineEnd());
		printf(("  [%s"), lineEnd());
		long long x = putFiles(argv[1], 1);
		if (x >= 0) {
			char *escapedPath = escapeName(argv[1]);
			printf(("  {\"directory\":true,\"path\":\"%s\",\"size\":%lld}%s"), escapedPath, x, lineEnd());
			free(escapedPath);
			printf(("  ]%s"), lineEnd());
			printf(("}%s"), lineEnd());
		}
	}
}
