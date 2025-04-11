import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { WebPage, SearchResponse, BrowsingState, BrowsingOptions, SearchOptions } from '../models/BrowsingModel';
import BrowsingModel from '../models/BrowsingModel';
import browsingController from '../controllers/BrowsingController';

interface BrowsingContextType {
  currentPage: WebPage | null;
  history: BrowsingState['history'];
  bookmarks: BrowsingState['bookmarks'];
  lastSearch: SearchResponse | null;
  loading: boolean;
  error: string | null;
  fetchPage: (url: string, options?: BrowsingOptions) => Promise<WebPage>;
  search: (query: string, options?: SearchOptions) => Promise<SearchResponse>;
  extractFinancialData: (url: string) => Promise<any>;
  addBookmark: (page: WebPage) => void;
  removeBookmark: (url: string) => void;
  clearHistory: () => void;
}

const BrowsingContext = createContext<BrowsingContextType | undefined>(undefined);

export const useBrowsing = () => {
  const context = useContext(BrowsingContext);
  if (!context) {
    throw new Error('useBrowsing must be used within a BrowsingProvider');
  }
  return context;
};

interface BrowsingProviderProps {
  children: ReactNode;
}

export const BrowsingProvider: React.FC<BrowsingProviderProps> = ({ children }) => {
  const [state, setState] = useState<BrowsingState>(BrowsingModel.createEmptyState());
  
  // Load browsing state from localStorage on mount
  useEffect(() => {
    try {
      const savedState = localStorage.getItem('browsingState');
      if (savedState) {
        const parsedState = JSON.parse(savedState);
        setState(prevState => ({
          ...prevState,
          history: parsedState.history || [],
          bookmarks: parsedState.bookmarks || []
        }));
      }
    } catch (error) {
      console.error('Error loading browsing state:', error);
    }
  }, []);
  
  // Save browsing state to localStorage when it changes
  useEffect(() => {
    try {
      const stateToSave = {
        history: state.history,
        bookmarks: state.bookmarks
      };
      localStorage.setItem('browsingState', JSON.stringify(stateToSave));
    } catch (error) {
      console.error('Error saving browsing state:', error);
    }
  }, [state.history, state.bookmarks]);
  
  const fetchPage = async (url: string, options?: BrowsingOptions): Promise<WebPage> => {
    setState(prevState => ({ ...prevState, loading: true, error: null }));
    
    try {
      const page = await browsingController.fetchPage(url, options);
      
      // Add to history
      const historyEntry = BrowsingModel.createBrowsingHistory(page.url, page.title);
      
      setState(prevState => ({
        ...prevState,
        currentPage: page,
        history: [historyEntry, ...prevState.history.filter(h => h.url !== url).slice(0, 99)],
        loading: false
      }));
      
      return page;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
      setState(prevState => ({ ...prevState, loading: false, error: errorMessage }));
      throw error;
    }
  };
  
  const search = async (query: string, options?: SearchOptions): Promise<SearchResponse> => {
    setState(prevState => ({ ...prevState, loading: true, error: null }));
    
    try {
      const searchResponse = await browsingController.search(query, options);
      
      setState(prevState => ({
        ...prevState,
        lastSearch: searchResponse,
        loading: false
      }));
      
      return searchResponse;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
      setState(prevState => ({ ...prevState, loading: false, error: errorMessage }));
      throw error;
    }
  };
  
  const extractFinancialData = async (url: string): Promise<any> => {
    setState(prevState => ({ ...prevState, loading: true, error: null }));
    
    try {
      const financialData = await browsingController.extractFinancialData(url);
      
      setState(prevState => ({
        ...prevState,
        loading: false
      }));
      
      return financialData;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
      setState(prevState => ({ ...prevState, loading: false, error: errorMessage }));
      throw error;
    }
  };
  
  const addBookmark = (page: WebPage): void => {
    setState(prevState => ({
      ...prevState,
      bookmarks: [page, ...prevState.bookmarks.filter(b => b.url !== page.url)]
    }));
  };
  
  const removeBookmark = (url: string): void => {
    setState(prevState => ({
      ...prevState,
      bookmarks: prevState.bookmarks.filter(b => b.url !== url)
    }));
  };
  
  const clearHistory = (): void => {
    setState(prevState => ({
      ...prevState,
      history: []
    }));
  };
  
  const value = {
    currentPage: state.currentPage,
    history: state.history,
    bookmarks: state.bookmarks,
    lastSearch: state.lastSearch,
    loading: state.loading,
    error: state.error,
    fetchPage,
    search,
    extractFinancialData,
    addBookmark,
    removeBookmark,
    clearHistory
  };
  
  return <BrowsingContext.Provider value={value}>{children}</BrowsingContext.Provider>;
};

export default BrowsingProvider;
