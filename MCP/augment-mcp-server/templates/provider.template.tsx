import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ${name} } from '../models/types';
import ${name}Controller from '../controllers/${name.toLowerCase()}Controller';

interface ${name}ContextType {
  ${name.toLowerCase()}s: ${name}[];
  current${name}: ${name} | null;
  loading: boolean;
  error: string | null;
  getAll${name}s: () => Promise<void>;
  get${name}ById: (id: string) => Promise<void>;
  create${name}: (data: Omit<${name}, 'id' | 'createdAt' | 'updatedAt'>) => Promise<void>;
  update${name}: (id: string, data: Partial<${name}>) => Promise<void>;
  delete${name}: (id: string) => Promise<void>;
}

const ${name}Context = createContext<${name}ContextType | undefined>(undefined);

export const use${name} = () => {
  const context = useContext(${name}Context);
  if (context === undefined) {
    throw new Error('use${name} must be used within a ${name}Provider');
  }
  return context;
};

interface ${name}ProviderProps {
  children: ReactNode;
}

export const ${name}Provider: React.FC<${name}ProviderProps> = ({ children }) => {
  const [${name.toLowerCase()}s, set${name}s] = useState<${name}[]>([]);
  const [current${name}, setCurrent${name}] = useState<${name} | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const getAll${name}s = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await ${name}Controller.getAll${name}s();
      set${name}s(result);
    } catch (err) {
      console.error('Error fetching ${name.toLowerCase()}s:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const get${name}ById = async (id: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await ${name}Controller.get${name}ById(id);
      setCurrent${name}(result);
    } catch (err) {
      console.error(`Error fetching ${name.toLowerCase()} with ID ${id}:`, err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const create${name} = async (data: Omit<${name}, 'id' | 'createdAt' | 'updatedAt'>) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await ${name}Controller.create${name}(data);
      set${name}s(prev => [...prev, result]);
      setCurrent${name}(result);
    } catch (err) {
      console.error('Error creating ${name.toLowerCase()}:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const update${name} = async (id: string, data: Partial<${name}>) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await ${name}Controller.update${name}(id, data);
      set${name}s(prev => prev.map(item => item.id === id ? result : item));
      setCurrent${name}(result);
    } catch (err) {
      console.error(`Error updating ${name.toLowerCase()} with ID ${id}:`, err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const delete${name} = async (id: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const success = await ${name}Controller.delete${name}(id);
      if (success) {
        set${name}s(prev => prev.filter(item => item.id !== id));
        if (current${name}?.id === id) {
          setCurrent${name}(null);
        }
      }
    } catch (err) {
      console.error(`Error deleting ${name.toLowerCase()} with ID ${id}:`, err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Load initial data
  useEffect(() => {
    getAll${name}s();
  }, []);

  const value = {
    ${name.toLowerCase()}s,
    current${name},
    loading,
    error,
    getAll${name}s,
    get${name}ById,
    create${name},
    update${name},
    delete${name}
  };

  return <${name}Context.Provider value={value}>{children}</${name}Context.Provider>;
};
