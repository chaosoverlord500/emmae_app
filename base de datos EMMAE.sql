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
    apellido VARCHAR(100) NOT NULL,
    especialidad varchar(100) NOT NULL
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

-- ===========================================================================
-- TABLA 3: instrumentos 
-- ============================================================================
USE EMMAE_BASEDEDATOS;

CREATE TABLE IF NOT EXISTS instrumentos (
  id_instrumento INT AUTO_INCREMENT PRIMARY KEY,
  tipo_instrumento VARCHAR(100) NOT NULL,
  instrumento_en_prestamo BOOLEAN NOT NULL DEFAULT FALSE,
  estado VARCHAR(100) NOT NULL,
  fecha_prestamo DATE NULL,
  hora_prestamo TIME NULL,
  fecha_limite DATE NULL,
  hora_limite TIME NULL,
  id_estudiante INT NULL,
  id_docente INT NULL,
  CONSTRAINT fk_instrumentos_estudiante FOREIGN KEY (id_estudiante)
    REFERENCES estudiantes(id_estudiante) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_instrumentos_docente FOREIGN KEY (id_docente)
    REFERENCES docente(id_docente) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


