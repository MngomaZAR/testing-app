<?php
namespace App;

use PDO;
use PDOException;

class Database
{
    private $host = 'dpg-cqaervqju9rs73bii0r0-a';
    private $db = 'institutional_voting';
    private $user = 'sam';
    private $password = 'v8S9dzTLOTZkjvg1zS8O6g8IfwDXLwg2';
    public $pdo;

    public function __construct()
    {
        $dsn = "pgsql:host={$this->host};port=5432;dbname={$this->db};";
        try {
            $this->pdo = new PDO($dsn, $this->user, $this->password, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
        } catch (PDOException $e) {
            echo 'Connection failed: ' . $e->getMessage();
            // Consider logging the error and handling it appropriately
            // exit or redirect if connection fails in production
        }
    }
}
?>
