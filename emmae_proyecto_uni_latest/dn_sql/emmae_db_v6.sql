CREATE DATABASE IF NOT EXISTS EMMAE_BASEDEDATOS;
USE EMMAE_BASEDEDATOS;

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
    cedula_estudiante INT NOT NULL PRIMARY KEY,
    nombre_estudiante VARCHAR(100) NOT NULL,
    apellido_estudiante VARCHAR(100) NOT NULL,
    instrumento_estudiante VARCHAR(100) NOT NULL,
    tiene_piano_complementario BOOLEAN NOT NULL DEFAULT FALSE,
    estudiante_tiene_prestamo BOOLEAN NOT NULL DEFAULT FALSE,
    ano_cursante VARCHAR(20) NOT NULL,
    telefono_estudiante VARCHAR(20) NOT NULL,
    correo_estudiante VARCHAR(100) NOT NULL,
    telefono_representante VARCHAR(20) NULL,
    correo_representante VARCHAR(100) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE instrumentos (
    id_instrumento INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    tipo_instrumento VARCHAR(100) NOT NULL,
    instrumento_disponible BOOLEAN NOT NULL DEFAULT TRUE,
    estado_instrumento VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE material_de_apoyo (
    id_mda INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    tipo_mda VARCHAR(100) NOT NULL,
    mda_disponible BOOLEAN NOT NULL DEFAULT TRUE,
    estado_mda VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE salon (
    id_salon INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    salon_ocupado BOOLEAN NOT NULL DEFAULT FALSE,
    id_piano INT NULL,
    estado_salon VARCHAR(100) NOT NULL,
    salon_disponible BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE prestamo (
    id_prestamo INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    cedula_estudiante INT NULL,
    cedula_docente INT NULL,
    id_instrumento INT NULL,
    id_mda INT NULL,
    id_salon INT NULL,
    fecha_prestamo DATE NOT NULL,
    fecha_limite_prestamo DATE NOT NULL,
    fecha_devolucion DATE NULL,
    estado ENUM('Pendiente','Prestado','Devuelto','Vencido') NOT NULL DEFAULT 'Prestado',
    observacion VARCHAR(255) NULL,
    FOREIGN KEY (cedula_estudiante) REFERENCES estudiante(cedula_estudiante),
    FOREIGN KEY (cedula_docente) REFERENCES docente(cedula_docente),
    FOREIGN KEY (id_instrumento) REFERENCES instrumentos(id_instrumento),
    FOREIGN KEY (id_mda) REFERENCES material_de_apoyo(id_mda),
    FOREIGN KEY (id_salon) REFERENCES salon(id_salon)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;