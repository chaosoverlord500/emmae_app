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
    especialidad VARCHAR(100) NOT NULL,
    tiene_prestamo BOOLEAN NOT NULL DEFAULT FALSE,
    correo VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE estudiantes (
    id_estudiante INT AUTO_INCREMENT PRIMARY KEY,
    cedula_estudiante INT,
    nombre_estudiante VARCHAR(100) NOT NULL,
    apellido_estudiante VARCHAR(100) NOT NULL,
    instrumento VARCHAR(100) NOT NULL,
    piano_comp BOOLEAN NOT NULL DEFAULT FALSE,
    tiene_prestamo BOOLEAN NOT NULL DEFAULT FALSE,
    ano_cursante VARCHAR(20),
    telefono_est VARCHAR(20) NOT NULL,
    correo_est VARCHAR(100) NOT NULL,
    telefono_rep VARCHAR(20) NULL,
    correo_rep VARCHAR(100) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
-- ===========================================================================
-- TABLA 3: instrumentos 
-- ============================================================================


CREATE TABLE IF NOT EXISTS instrumentos (
  id_instrumento INT NOT NULL auto_increment,
  tipo_instrumento VARCHAR(100) NOT NULL,
  instrumento_en_prest BOOLEAN NOT NULL DEFAULT FALSE,
  estado VARCHAR(100) NOT NULL,
  fecha_prest_instrumetnto DATE NULL,
  hora_prest_instrumetnto TIME NULL,
  fecha_limite_instrumetnto DATE NULL,
  hora_limite_instrumetnto TIME NULL,
  id_estudiante INT NULL,
  cedula_docente INT NULL,
  CONSTRAINT fk_instrumentos_estudiante FOREIGN KEY (id_estudiante)
    REFERENCES estudiantes(id_estudiante) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_instrumentos_docente FOREIGN KEY (cedula_docente)
    REFERENCES docente(cedula_docente) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================================0
-- TABLA 4: material de apoyo
-- =======================================================================0
USE EMMAE_BASEDEDATOS;

CREATE TABLE material (
  id_m_a INT NOT NULL auto_increment,
  tipo_material VARCHAR(100) NOT NULL,
  material_en_prest BOOLEAN NOT NULL DEFAULT FALSE,
  estado_material VARCHAR(100),
  fecha_prest_m_a DATE NULL,
  hora_prest_m_a TIME NULL,
  fecha_limite_m_a DATE NULL,
  hora_limite_m_a TIME NULL,
  id_estudiante INT NULL,
  cedula_docente INT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===========================================================================0
-- tabla 5: salones
-- ==================================================================0

USE EMMAE_BASEDEDATOS;

CREATE TABLE IF NOT EXISTS salones (
  id_salon INT NOT NULL PRIMARY KEY,
  salon_ocupado BOOLEAN NOT NULL DEFAULT FALSE,
  tiene_piano BOOLEAN NOT NULL DEFAULT FALSE,
  estado VARCHAR(100) NOT NULL ,
  fecha_prest DATE NULL,
  hora_prest TIME NULL,
  fecha_limite_prest DATE NULL,
  hora_limite_prest TIME NULL,
  cedula_docente_ocupante INT NULL,
  ya_en_prest BOOLEAN NOT NULL DEFAULT FALSE,
  estado_piano VARCHAR(100), 
  id_estudiante_ocu INT NULL,
  especialidad_docente VARCHAR(100) NULL,
  CONSTRAINT fk_salon_docente FOREIGN KEY (cedula_docente_ocupante)
    REFERENCES docente(cedula_docente) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_salon_estudiante FOREIGN KEY (id_estudiante_ocupante)
    REFERENCES estudiantes(id_estudiante) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE docente

ADD COLUMN tiene_prestamo BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN correo VARCHAR(100) NOT NULL,
ADD COLUMN telefono VARCHAR(20) NULL;