<?php
session_start();
require 'db.php';

use App\Database;

$db = new Database();

if (!isset($_SESSION['user_id'])) {
    header("Location: auth.php");
    exit();
}

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $candidate_id = $_POST['candidate'];
    $user_id = $_SESSION['user_id'];

    $db->pdo->beginTransaction();
    try {
        $stmt = $db->pdo->prepare("UPDATE users SET is_voted = TRUE WHERE id = :user_id AND is_voted = FALSE");
        $stmt->execute(['user_id' => $user_id]);

        if ($stmt->rowCount() > 0) {
            $stmt = $db->pdo->prepare("INSERT INTO votes (user_id, candidate_id) VALUES (:user_id, :candidate_id)");
            $stmt->execute(['user_id' => $user_id, 'candidate_id' => $candidate_id]);

            $stmt = $db->pdo->prepare("UPDATE candidates SET votes = votes + 1 WHERE id = :candidate_id");
            $stmt->execute(['candidate_id' => $candidate_id]);

            $db->pdo->commit();
            echo "Vote successfully cast!";
            // Optionally, redirect to a results page or display a success message
        } else {
            echo "You have already voted!";
            // Handle case where user has already voted
        }
    } catch (PDOException $e) {
        $db->pdo->rollBack();
        echo "Failed to cast vote: " . $e->getMessage();
        // Log the error and handle it appropriately
    }
    exit();
}

$stmt = $db->pdo->query("SELECT * FROM candidates");
$candidates = $stmt->fetchAll();
?>
<!DOCTYPE html>
<html>
<head>
    <title>Vote</title>
    <link rel="stylesheet" type="text/css" href="css/styles.css">
</head>
<body>
    <form method="post" action="vote.php">
        <h1>Vote for your candidate</h1>
        <?php foreach ($candidates as $candidate): ?>
            <div>
                <input type="radio" id="candidate<?php echo $candidate['id']; ?>" name="candidate" value="<?php echo $candidate['id']; ?>" required>
                <label for="candidate<?php echo $candidate['id']; ?>">
                    <img src="<?php echo $candidate['picture_url']; ?>" alt="<?php echo $candidate['name']; ?>" width="100" height="100">
                    <?php echo $candidate['name']; ?>
                </label>
            </div>
        <?php endforeach; ?>
        <button type="submit">Submit Vote</button>
    </form>
</body>
</html>
