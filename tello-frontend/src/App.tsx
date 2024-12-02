// src/App.tsx
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from '@/components/ui/toaster';
import DroneController from './components/DroneController';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
        <main className="container mx-auto py-6">
          <DroneController />
        </main>
      </div>
      <Toaster />
    </QueryClientProvider>
  );
}

export default App;