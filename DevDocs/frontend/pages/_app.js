import '../styles/globals.css';
import { AuthProvider } from '../providers/AuthProvider';
import { DocumentProvider } from '../providers/DocumentProvider';

function MyApp({ Component, pageProps }) {
  return (
    <AuthProvider>
      <DocumentProvider>
        <Component {...pageProps} />
      </DocumentProvider>
    </AuthProvider>
  );
}

export default MyApp;
