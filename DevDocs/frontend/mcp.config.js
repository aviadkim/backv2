module.exports = {
  // Project name
  name: 'findoc',
  
  // Base directory for all generated files
  baseDir: './',
  
  // Structure configuration
  structure: {
    // Models configuration
    models: {
      dir: './models',
      template: './templates/model.template.ts',
      extension: '.ts'
    },
    
    // Controllers configuration
    controllers: {
      dir: './controllers',
      template: './templates/controller.template.ts',
      extension: '.ts'
    },
    
    // Providers configuration
    providers: {
      dir: './providers',
      template: './templates/provider.template.tsx',
      extension: '.tsx'
    },
    
    // Repositories configuration
    repositories: {
      dir: './repositories',
      template: './templates/repository.template.ts',
      extension: '.ts'
    }
  },
  
  // TypeScript configuration
  typescript: {
    enabled: true,
    strict: true
  },
  
  // Linting configuration
  linting: {
    eslint: true,
    prettier: true
  }
}
