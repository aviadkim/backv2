import '../styles/globals.css';
import { useState, useEffect } from 'react';
import { AuthProvider } from '../providers/AuthProvider';
import { DocumentProvider } from '../providers/DocumentProvider';
import Layout from '../components/Layout';
import SimpleWrapper from '../components/SimpleWrapper';
import RouterWrapper from '../components/RouterWrapper';
import FontLoader from '../components/FontLoader';

function MyApp({ Component, pageProps }) {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Set loading to false after a short delay
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700">Loading DevDocs...</h2>
          <p className="text-gray-500 mt-2">Please wait while we prepare your experience</p>
        </div>
      </div>
    );
  }

  // Check if the page should use the layout
  const getLayout = Component.getLayout || ((page) => <Layout>{page}</Layout>);

  return (
    <SimpleWrapper>
      <FontLoader />
      <RouterWrapper>
        <AuthProvider>
          <DocumentProvider>
            {getLayout(<Component {...pageProps} />)}
          </DocumentProvider>
        </AuthProvider>
      </RouterWrapper>
    </SimpleWrapper>
  );
}

export default MyApp;
