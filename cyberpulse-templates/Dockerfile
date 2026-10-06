# Usa una imagen ligera de Node
FROM node:20-alpine

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de dependencias
COPY package.json package-lock.json* ./

# Instala las dependencias
RUN npm install

# Copia el resto del código del frontend
COPY . .

# Expone el puerto que usa Vite
EXPOSE 5173

# Comando para iniciar en modo host para que el contenedor de Python lo alcance
CMD ["npm", "run", "dev", "--", "--host"]