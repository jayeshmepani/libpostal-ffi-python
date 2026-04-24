#!/usr/bin/env php
<?php

$postalkitVersion = "v1.0.3";
$repoUrl = "https://github.com/jayeshmepani/libpostal-ffi-python/releases/download/{$postalkitVersion}";

$targets = [
    'linux-x64' => 'libpostal-linux-x64.tar.gz',
    'linux-arm64' => 'libpostal-linux-arm64.tar.gz',
    'macos-x64' => 'libpostal-macos-x64.tar.gz',
    'macos-arm64' => 'libpostal-macos-arm64.tar.gz',
    'windows-x64' => 'libpostal-windows-x64.zip',
];

$libsDir = dirname(__DIR__) . '/postalkit/libs';

foreach ($targets as $target => $filename) {
    $targetDir = "{$libsDir}/{$target}";
    if (!is_dir($targetDir)) {
        mkdir($targetDir, 0777, true);
    }

    $url = "{$repoUrl}/{$filename}";
    $dest = "{$targetDir}/{$filename}";

    echo "Downloading {$url}...\n";
    $content = file_get_contents($url);
    if ($content === false) {
        echo "Failed to download {$url}. Skipping.\n";
        continue;
    }

    file_put_contents($dest, $content);

    echo "Extracting {$dest}...\n";
    if (str_ends_with($filename, '.zip')) {
        $zip = new ZipArchive;
        if ($zip->open($dest) === TRUE) {
            $zip->extractTo($targetDir);
            $zip->close();
        } else {
            echo "Failed to extract zip.\n";
        }
    } else {
        exec("tar -xzf " . escapeshellarg($dest) . " -C " . escapeshellarg($targetDir));
    }

    unlink($dest);
    echo "Successfully setup {$target}\n";
}
