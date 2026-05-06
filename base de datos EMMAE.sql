-- ============================================================
-- BASE DE DATOS: EMMAE_BASEDEDATOS
-- Escuela de Música - Docentes y Estudiantes
-- ============================================================

-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS EMMAE_BASEDEDATOS;
USE EMMAE_BASEDEDATOS;

-- ============================================================
-- TABLA 1: docente
-- ============================================================
CREATE TABLE docente (
    id_docente INT AUTO_INCREMENT PRIMARY KEY,
    cedula INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- TABLA 2: estudiantes
-- ============================================================
CREATE TABLE estudiantes (
    id_estudiante INT AUTO_INCREMENT PRIMARY KEY,
    cedula INT,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    instrumento VARCHAR(100) NOT NULL,
    piano_complementario BOOLEAN NOT NULL DEFAULT FALSE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;