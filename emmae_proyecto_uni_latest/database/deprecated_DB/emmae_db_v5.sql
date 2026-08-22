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
    cedula_docente INT NOT NULL PRIMARY KEY,
    nombre_docente VARCHAR(100) NOT NULL,
    apellido_docente VARCHAR(100) NOT NULL,
    especialidad_primaria VARCHAR(100) NOT NULL,
    docente_tiene_prestamo BOOLEAN NOT NULL DEFAULT FALSE,
    correo_docente VARCHAR(100) NOT NULL,
    telefono_docente VARCHAR(20) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE estudiante (
    cedula_estudiante INT,
    nombre_estudiante VARCHAR(100) NOT NULL,
    apellido_estudiante VARCHAR(100) NOT NULL,
    instrumento_estudiante VARCHAR(100) NOT NULL,
    tiene_piano_complementario BOOLEAN NOT NULL DEFAULT FALSE,
    estudiante_tiene_prestamo BOOLEAN NOT NULL DEFAULT FALSE,
    ano_cursante VARCHAR(20),
    telefono_estudiante VARCHAR(20) NOT NULL,
    correo_estudiante VARCHAR(100) NOT NULL,
    telefono_representante VARCHAR(20) NULL,
    correo_representante VARCHAR(100) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- ===========================================================================
-- TABLA 3: instrumentos 
-- ============================================================================


CREATE TABLE IF NOT EXISTS instrumentos (
  id_instrumento INT NOT NULL auto_increment,
  tipo_instrumento VARCHAR(100) NOT NULL,
  instrumento_disponible BOOLEAN NOT NULL DEFAULT FALSE,
  estado_instrumento VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================================0
-- TABLA 4: material de apoyo
-- =======================================================================0

CREATE TABLE material_de_apoyo (
  id_mda INT NOT NULL auto_increment,
  tipo_mda VARCHAR(100) NOT NULL,
  mda_disponible BOOLEAN NOT NULL DEFAULT FALSE,
  estado_mda VARCHAR(100),
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===========================================================================0
-- tabla 5: salones
-- ==================================================================0

CREATE TABLE IF NOT EXISTS salon (
  id_salon INT NOT NULL PRIMARY KEY,
  salon_ocupado BOOLEAN NOT NULL DEFAULT FALSE,
  id_piano INT NULL,
  estado_salon VARCHAR(100) NOT NULL ,
  salon_disponible BOOLEAN NOT NULL DEFAULT FALSE,
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==============================
-- TABLA DE PRESTAMOS
-- ==============================

CREATE TABLE IF NOT EXISTS prestamo(
  id_prestamo INT PRIMARY KEY auto_increment,
  id_instrumento INT NULL,
  id_mda INT NULL,
  id_salon INT NULL,
  cedula_estudiante INT NULL,
  cedula_docente INT NULL,
  fecha_prestamo TIME NULL,
  fecha_limite_prestamo TIME NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;