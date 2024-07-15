<?php
session_start();
require '../src/db.php';

use App\Database;

$db = new Database();

$response = '';

if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_FILES['picture'])) {
    $name = $_POST['name'];
    $picture = $_FILES['picture'];
    $target_dir = "../uploads/";
    $target_file = $target_dir . basename($picture['name']);
    move_uploaded_file($picture['tmp_name'], $target_file);

    $stmt = $db->pdo->prepare("INSERT INTO candidates (name, picture_url) VALUES (:name, :picture_url)");
    $stmt->execute(['name' => $name, 'picture_url' => $target_file]);
    echo "Candidate added successfully!";
    // Optionally, redirect to a candidates list or display a success message
}

$stmt = $db->pdo->query("SELECT * FROM candidates");
$candidates = $stmt->fetchAll();
?>
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
    <link rel="stylesheet" type="text/css" href="../css/styles.css">
</head>
<body>
    <h1>Admin Panel</h1>
    <form method="post" action="index.php" enctype="multipart/form-data">
        <label for="name">Candidate Name:</label>
        <input type="text" id="name" name="name" required>
        <label for="picture">Picture:</label>
        <input type="file" id="picture" name="picture" required>
        <button type="submit">Add Candidate</button>
    </form>
    <h2>Candidates</h2>
    <ul>
        <?php foreach ($candidates as $candidate): ?>
            <li>
                <img src="<?php echo $candidate['picture_url']; ?>" alt="<?php echo $candidate['name']; ?>" width="100" height="100">
                <?php echo $candidate['name']; ?>
            </li>
        <?php endforeach; ?>
    </ul>
</body>
</html>
