<?php
session_start();
require 'db.php';

use App\Database;

$db = new Database();

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $student_id = $_POST['student_id'];
    $pin = $_POST['pin'];

    $stmt = $db->pdo->prepare("SELECT * FROM users WHERE student_id = :student_id AND pin = :pin");
    $stmt->execute(['student_id' => $student_id, 'pin' => $pin]);
    $user = $stmt->fetch();

    if ($user) {
        $_SESSION['user_id'] = $user['id'];
        header("Location: vote.php");
        exit();
    } else {
        echo "Invalid credentials";
        // You might want to redirect or display a proper error message
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <link rel="stylesheet" type="text/css" href="css/styles.css">
</head>
<body>
    <form method="post" action="auth.php">
        <label for="student_id">Student ID:</label>
        <input type="text" id="student_id" name="student_id" required>
        <label for="pin">PIN:</label>
        <input type="password" id="pin" name="pin" required>
        <button type="submit">Login</button>
    </form>
</body>
</html>
