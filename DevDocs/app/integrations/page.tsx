import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch"; // Assuming Switch component exists or will be added

// Placeholder Icon
const ExternalLinkIcon = ({ className }: { className?: string }) => (
 <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className || "h-4 w-4"}><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
);

export default function IntegrationsPage() {
  // Placeholder state for integrations
  const integrations = [
    { id: 'aws-s3', name: 'AWS S3 Storage', description: 'Connect your AWS S3 bucket for document storage.', connected: true },
    { id: 'google-drive', name: 'Google Drive', description: 'Sync documents with your Google Drive account.', connected: false },
    { id: 'quickbooks', name: 'QuickBooks Online', description: 'Export financial data to QuickBooks.', connected: false },
  ];

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold text-slate-800">Integrations</h1>

      <Card>
        <CardHeader>
          <CardTitle>Connect External Systems</CardTitle>
          <CardDescription>Manage connections to external services like cloud storage and accounting software.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {integrations.map((integration) => (
            <Card key={integration.id} className="flex items-center justify-between p-4">
              <div className="flex items-center gap-4">
                 {/* Placeholder Icon */}
                 <div className="h-10 w-10 rounded-lg bg-slate-100 flex items-center justify-center">
                    <ExternalLinkIcon className="h-5 w-5 text-slate-500"/>
                 </div>
                 <div>
                    <h3 className="font-medium">{integration.name}</h3>
                    <p className="text-sm text-slate-500">{integration.description}</p>
                 </div>
              </div>
              <div className="flex items-center gap-2">
                 {/* TODO: Add Switch component if needed, or use Button */}
                 {/* <Switch checked={integration.connected} onCheckedChange={() => {}} /> */}
                 <Button variant={integration.connected ? "outline" : "default"}>
                    {integration.connected ? 'Disconnect' : 'Connect'}
                 </Button>
              </div>
            </Card>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}