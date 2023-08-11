<?php
if(isset($_GET['file'])) {
    $filePath = $_GET['file'];

    // Check if the file exists
    if(file_exists($filePath)) {
        // Set appropriate headers for the download
        header("Content-Type: application/octet-stream");
        header("Content-Disposition: attachment; filename=" . basename($filePath));
        header("Content-Length: " . filesize($filePath));
        
        // Read the file and output it to the user
        readfile($filePath);
        exit;
    } else {
        echo "File not found.";
    }
}
?>
