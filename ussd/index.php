<?php
require '../src/db.php';

use App\Database;

$db = new Database();

$response = '';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $sessionId = $_POST['sessionId'];
    $serviceCode = $_POST['serviceCode'];
    $phoneNumber = $_POST['phoneNumber'];
    $text = $_POST['text'];

    $textArray = explode('*', $text);
    $userResponse = trim(end($textArray));

    switch (count($textArray)) {
        case 1:
            $response .= "CON Welcome to the Voting System\n";
            $response .= "1. Login\n";
            break;
        case 2:
            if ($userResponse == "1") {
                $response .= "CON Enter your Student ID\n";
            } else {
                $response .= "END Invalid choice";
            }
            break;
        case 3:
            $student_id = $userResponse;
            $response .= "CON Enter your PIN\n";
            break;
        case 4:
            $pin = $userResponse;
            $stmt = $db->pdo->prepare("SELECT * FROM users WHERE student_id = :student_id AND pin = :pin");
            $stmt->execute(['student_id' => $textArray[2], 'pin' => $pin]);
            $user = $stmt->fetch();

            if ($user) {
                $response .= "CON Choose a candidate\n";
                $stmt = $db->pdo->query("SELECT * FROM candidates");
                while ($row = $stmt->fetch()) {
                    $response .= "{$row['id']}. {$row['name']}\n";
                }
            } else {
                $response .= "END Invalid credentials";
            }
            break;
        case 5:
            $candidate_id = $userResponse;
            $user_id = $user['id'];

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
                    $response .= "END Vote successfully cast!";
                } else {
                    $response .= "END You have already voted!";
                }
            } catch (Exception $e) {
                $db->pdo->rollBack();
                $response .= "END Failed to cast vote: " . $e->getMessage();
            }
            break;
        default:
            $response .= "END Invalid input";
    }

    header('Content-type: text/plain');
    echo $response;
    exit();
}
?>
