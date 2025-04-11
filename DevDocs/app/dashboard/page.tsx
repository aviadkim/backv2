import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

// Placeholder Icons - replace later
const IconPlaceholder = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className || "h-4 w-4"}><path d="M12 5v14M5 12h14" /></svg>
);
const ArrowUpIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className || "h-4 w-4"}><path d="M12 19V5M5 12l7-7 7 7" /></svg>
);


export default function DashboardPage() {
  // Placeholder data - replace with actual data fetching later
  const stats = [
    { title: "Total Documents", value: "37", change: "+24%", changeColor: "text-green-600", iconBg: "bg-indigo-100", iconColor: "text-indigo-600" },
    { title: "Total Pages", value: "243", change: "+12%", changeColor: "text-green-600", iconBg: "bg-green-100", iconColor: "text-green-600" },
    { title: "ISIN Numbers", value: "93", change: "+18%", changeColor: "text-amber-600", iconBg: "bg-amber-100", iconColor: "text-amber-600" },
  ];

  const recentDocuments = [
    { name: "Q4 Financial Report 2024.pdf", date: "Mar 24, 2025", type: "Financial", pages: 12, iconColor: "text-indigo-600", iconBg: "bg-indigo-100" },
    { name: "Investment Portfolio Summary.pdf", date: "Mar 22, 2025", type: "Portfolio", pages: 8, iconColor: "text-amber-600", iconBg: "bg-amber-100" },
    { name: "Bank Statement March 2025.pdf", date: "Mar 20, 2025", type: "Banking", pages: 4, iconColor: "text-green-600", iconBg: "bg-green-100" },
  ];

   const isinAnalysis = [
    { isin: "US0378331005", description: "Apple Inc.", document: "Investment Portfolio Summary", value: "$176.35", valueColor: "text-green-600" },
    { isin: "US5949181045", description: "Microsoft Corporation", document: "Investment Portfolio Summary", value: "$412.27", valueColor: "text-green-600" },
  ];


  return (
    <div className="flex flex-col gap-6">
      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">{stat.title}</CardTitle>
              <div className={`flex items-center justify-center h-10 w-10 rounded-full ${stat.iconBg}`}>
                 <IconPlaceholder className={`h-5 w-5 ${stat.iconColor}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900">{stat.value}</div>
              <p className={`text-xs ${stat.changeColor} flex items-center`}>
                <ArrowUpIcon className="h-3 w-3 mr-1"/>
                {stat.change} from last month
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Documents Table */}
      <div>
        <h2 className="text-lg font-semibold mb-3 text-slate-800">Recent Documents</h2>
        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[50px]"></TableHead>
                <TableHead>Document Name</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Pages</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {recentDocuments.map((doc) => (
                <TableRow key={doc.name}>
                  <TableCell>
                     <div className={`flex items-center justify-center h-8 w-8 rounded-full ${doc.iconBg}`}>
                        <IconPlaceholder className={`h-4 w-4 ${doc.iconColor}`} />
                     </div>
                  </TableCell>
                  <TableCell className="font-medium text-slate-800">{doc.name}</TableCell>
                  <TableCell className="text-slate-600">{doc.date}</TableCell>
                  <TableCell><Badge variant="secondary">{doc.type}</Badge></TableCell>
                  <TableCell className="text-slate-600">{doc.pages}</TableCell>
                  <TableCell className="text-right">
                    {/* Placeholder Action Buttons */}
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <IconPlaceholder className="h-4 w-4 text-slate-500" />
                    </Button>
                     <Button variant="ghost" size="icon" className="h-8 w-8">
                      <IconPlaceholder className="h-4 w-4 text-slate-500" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </div>

       {/* ISIN Analysis Table */}
      <div>
        <h2 className="text-lg font-semibold mb-3 text-slate-800">ISIN Analysis</h2>
        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ISIN</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Document</TableHead>
                <TableHead>Value</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isinAnalysis.map((item) => (
                <TableRow key={item.isin}>
                  <TableCell className="font-medium text-slate-800">{item.isin}</TableCell>
                  <TableCell className="text-slate-600">{item.description}</TableCell>
                  <TableCell className="text-slate-800">{item.document}</TableCell>
                  <TableCell className={item.valueColor}>{item.value}</TableCell>
                   <TableCell className="text-right">
                    {/* Placeholder Action Buttons */}
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <IconPlaceholder className="h-4 w-4 text-slate-500" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </div>

    </div>
  );
}