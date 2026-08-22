-- ============================================================
-- BASE DE DATOS: EMMAE_DB
-- Escuela de Música - Docentes y Estudiantes
-- ============================================================

-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS EMMAE_DB;
USE EMMAE_DB;

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


CREATE TABLE IF NOT EXISTS instrumentos (
  id_instrumento INT AUTO_INCREMENT PRIMARY KEY,
  tipo_instrumento VARCHAR(100) NOT NULL,
  instrumento_en_prestamo BOOLEAN NOT NULL DEFAULT FALSE,
  estado VARCHAR(100) NOT NULL,
  fecha_prestamo_instrumetnto DATE NULL,
  hora_prestamo_instrumetnto TIME NULL,
  fecha_limite_instrumetnto DATE NULL,
  hora_limite_instrumetnto TIME NULL,
  id_estudiante INT NULL,
  id_docente INT NULL,
  CONSTRAINT fk_instrumentos_estudiante FOREIGN KEY (id_estudiante)
    REFERENCES estudiantes(id_estudiante) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_instrumentos_docente FOREIGN KEY (id_docente)
    REFERENCES docente(id_docente) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================================0
-- TABLA 4: material de apoyo
-- =======================================================================0
USE EMMAE_BASEDEDATOS;

CREATE TABLE material (
  id_material_apoyo INT AUTO_INCREMENT PRIMARY KEY,
  tipo_material VARCHAR(100) NOT NULL,
  material_en_prestamo BOOLEAN NOT NULL DEFAULT FALSE,
  estado_material VARCHAR(100),
  fecha_prestamo_material DATE NULL,
  hora_prestamo_material TIME NULL,
  fecha_limite_material DATE NULL,
  hora_limite_material TIME NULL,
  id_estudiante INT NULL,
  id_docente INT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===========================================================================0
-- tabla 5: salones
-- ==================================================================0

USE EMMAE_BASEDEDATOS;

CREATE TABLE IF NOT EXISTS salones (
  id_salon INT AUTO_INCREMENT PRIMARY KEY,
  salon_ocupado BOOLEAN NOT NULL DEFAULT FALSE,
  tiene_piano BOOLEAN NOT NULL DEFAULT FALSE,
  estado VARCHAR(100) NOT NULL ,
  fecha_prestamo DATE NULL,
  hora_prestamo TIME NULL,
  fecha_limite_prestamo DATE NULL,
  hora_limite_prestamo TIME NULL,
  id_docente_ocupante INT NULL,
  ya_en_prestamo BOOLEAN NOT NULL DEFAULT FALSE,
  estado_piano VARCHAR(100), 
  id_estudiante_ocupante INT NULL,
  especialidad_docente VARCHAR(100) NULL,
  CONSTRAINT fk_salon_docente FOREIGN KEY (id_docente_ocupante)
    REFERENCES docente(id_docente) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_salon_estudiante FOREIGN KEY (id_estudiante_ocupante)
    REFERENCES estudiantes(id_estudiante) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;