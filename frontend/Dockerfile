# Use official Node runtime as parent image
FROM node:22-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy project
COPY . .

# Build the application
RUN npm run build

# Start the application
CMD ["npm", "start"]
