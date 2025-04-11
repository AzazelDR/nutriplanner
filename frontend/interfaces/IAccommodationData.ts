export interface IAccommodationData {
  id: number;
  nombre: string;
  descripcion: string;
  duracion: string;
  macros: {
    carbohidratos: string;
    proteinas: string;
    grasas: string;
  };
  alimentos_clave: string[];
  evitar: string[];
  lugar_referencia: {
    nombre: string;
    ubicacion: string;
    contacto: string;
  };
}