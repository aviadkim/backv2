import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

export default function SettingsPage() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold text-slate-800">Settings</h1>

      <Card>
        <CardHeader>
          <CardTitle>Application Settings</CardTitle>
          <CardDescription>Configure system preferences, extraction parameters, and language settings.</CardDescription>
        </CardHeader>
        <CardContent>
          {/* TODO: Implement settings form sections */}
          <p className="text-slate-500">Settings content will go here...</p>
          <div className="mt-4 space-y-4">
             <div className="p-4 border rounded bg-slate-50">Processing Preferences Placeholder</div>
             <div className="p-4 border rounded bg-slate-50">Language Settings Placeholder</div>
             <div className="p-4 border rounded bg-slate-50">Account Settings Placeholder</div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}