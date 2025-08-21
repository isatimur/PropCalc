"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { 
  Settings, 
  User, 
  Shield, 
  Bell, 
  Database, 
  Globe,
  Download,
  Upload,
  Save,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  Eye,
  EyeOff,
  Key,
  Mail,
  Phone,
  MapPin,
  Building2,
  DollarSign,
  BarChart3,
  FileText,
  Calendar,
  Zap,
  Palette,
  Monitor,
  Smartphone,
  Tablet
} from "lucide-react";

interface UserSettings {
  profile: {
    firstName: string;
    lastName: string;
    email: string;
    phone: string;
    company: string;
    role: string;
    avatar: string;
  };
  preferences: {
    language: string;
    timezone: string;
    currency: string;
    dateFormat: string;
    theme: 'light' | 'dark' | 'auto';
    notifications: {
      email: boolean;
      push: boolean;
      sms: boolean;
      marketUpdates: boolean;
      priceAlerts: boolean;
      reportReady: boolean;
    };
  };
  dataSettings: {
    refreshInterval: number;
    autoExport: boolean;
    exportFormat: string;
    dataRetention: number;
    maxDataPoints: number;
  };
  security: {
    twoFactorEnabled: boolean;
    sessionTimeout: number;
    passwordExpiry: number;
    loginNotifications: boolean;
  };
}

export default function DLDSettingsPage() {
  const [settings, setSettings] = useState<UserSettings>({
    profile: {
      firstName: 'John',
      lastName: 'Doe',
      email: 'john.doe@company.com',
      phone: '+971 50 123 4567',
      company: 'Real Estate Analytics Ltd',
      role: 'Senior Analyst',
      avatar: '/avatars/john-doe.jpg'
    },
    preferences: {
      language: 'en',
      timezone: 'Asia/Dubai',
      currency: 'AED',
      dateFormat: 'DD/MM/YYYY',
      theme: 'auto',
      notifications: {
        email: true,
        push: true,
        sms: false,
        marketUpdates: true,
        priceAlerts: true,
        reportReady: true
      }
    },
    dataSettings: {
      refreshInterval: 15,
      autoExport: false,
      exportFormat: 'PDF',
      dataRetention: 365,
      maxDataPoints: 10000
    },
    security: {
      twoFactorEnabled: false,
      sessionTimeout: 30,
      passwordExpiry: 90,
      loginNotifications: true
    }
  });

  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'ar', name: 'العربية' },
    { code: 'fr', name: 'Français' },
    { code: 'de', name: 'Deutsch' },
    { code: 'es', name: 'Español' }
  ];

  const timezones = [
    { value: 'Asia/Dubai', label: 'Dubai (GMT+4)' },
    { value: 'Asia/Abu_Dhabi', label: 'Abu Dhabi (GMT+4)' },
    { value: 'Europe/London', label: 'London (GMT+0)' },
    { value: 'America/New_York', label: 'New York (GMT-5)' },
    { value: 'Asia/Singapore', label: 'Singapore (GMT+8)' }
  ];

  const currencies = [
    { code: 'AED', name: 'UAE Dirham (AED)' },
    { code: 'USD', name: 'US Dollar (USD)' },
    { code: 'EUR', name: 'Euro (EUR)' },
    { code: 'GBP', name: 'British Pound (GBP)' },
    { code: 'SAR', name: 'Saudi Riyal (SAR)' }
  ];

  const dateFormats = [
    { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY' },
    { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY' },
    { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD' },
    { value: 'DD-MM-YYYY', label: 'DD-MM-YYYY' }
  ];

  const exportFormats = [
    { value: 'PDF', label: 'PDF Document' },
    { value: 'Excel', label: 'Excel Spreadsheet' },
    { value: 'CSV', label: 'CSV Data' },
    { value: 'JSON', label: 'JSON Data' }
  ];

  const handleSave = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileUpdate = (field: string, value: string) => {
    setSettings(prev => ({
      ...prev,
      profile: { ...prev.profile, [field]: value }
    }));
  };

  const handlePreferenceUpdate = (field: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      preferences: { ...prev.preferences, [field]: value }
    }));
  };

  const handleNotificationUpdate = (field: string, value: boolean) => {
    setSettings(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        notifications: { ...prev.preferences.notifications, [field]: value }
      }
    }));
  };

  const handleDataSettingUpdate = (field: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      dataSettings: { ...prev.dataSettings, [field]: value }
    }));
  };

  const handleSecurityUpdate = (field: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      security: { ...prev.security, [field]: value }
    }));
  };

  const exportSettings = () => {
    const dataStr = JSON.stringify(settings, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'dld-settings.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  const importSettings = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const importedSettings = JSON.parse(e.target?.result as string);
          setSettings(importedSettings);
        } catch (error) {
          console.error('Failed to parse settings file:', error);
        }
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">DLD Settings</h1>
        <p className="text-gray-600">Configure your account preferences, data settings, and security options</p>
      </div>

      {/* Quick Actions */}
      <div className="flex flex-wrap gap-4 mb-6">
        <Button onClick={handleSave} disabled={loading} className="flex items-center gap-2">
          <Save className="h-4 w-4" />
          {loading ? 'Saving...' : 'Save Changes'}
        </Button>
        <Button variant="outline" onClick={exportSettings}>
          <Download className="h-4 w-4 mr-2" />
          Export Settings
        </Button>
        <Button variant="outline" asChild>
          <label className="cursor-pointer">
            <Upload className="h-4 w-4 mr-2" />
            Import Settings
            <input
              type="file"
              accept=".json"
              onChange={importSettings}
              className="hidden"
            />
          </label>
        </Button>
        {saved && (
          <Badge className="bg-green-100 text-green-800 border-green-200">
            <CheckCircle className="h-4 w-4 mr-1" />
            Settings Saved
          </Badge>
        )}
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="profile" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="preferences" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Preferences
          </TabsTrigger>
          <TabsTrigger value="data" className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            Data
          </TabsTrigger>
          <TabsTrigger value="security" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Security
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Notifications
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Personal Information</CardTitle>
              <CardDescription>Update your personal details and contact information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="firstName">First Name</Label>
                  <Input
                    id="firstName"
                    value={settings.profile.firstName}
                    onChange={(e) => handleProfileUpdate('firstName', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input
                    id="lastName"
                    value={settings.profile.lastName}
                    onChange={(e) => handleProfileUpdate('lastName', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={settings.profile.email}
                    onChange={(e) => handleProfileUpdate('email', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input
                    id="phone"
                    value={settings.profile.phone}
                    onChange={(e) => handleProfileUpdate('phone', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="company">Company</Label>
                  <Input
                    id="company"
                    value={settings.profile.company}
                    onChange={(e) => handleProfileUpdate('company', e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="role">Job Role</Label>
                  <Input
                    id="role"
                    value={settings.profile.role}
                    onChange={(e) => handleProfileUpdate('role', e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="preferences" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Display & Language</CardTitle>
              <CardDescription>Customize your interface and regional settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="language">Language</Label>
                  <Select value={settings.preferences.language} onValueChange={(value) => handlePreferenceUpdate('language', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {languages.map((lang) => (
                        <SelectItem key={lang.code} value={lang.code}>
                          {lang.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="timezone">Timezone</Label>
                  <Select value={settings.preferences.timezone} onValueChange={(value) => handlePreferenceUpdate('timezone', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {timezones.map((tz) => (
                        <SelectItem key={tz.value} value={tz.value}>
                          {tz.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="currency">Currency</Label>
                  <Select value={settings.preferences.currency} onValueChange={(value) => handlePreferenceUpdate('currency', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {currencies.map((curr) => (
                        <SelectItem key={curr.code} value={curr.code}>
                          {curr.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="dateFormat">Date Format</Label>
                  <Select value={settings.preferences.dateFormat} onValueChange={(value) => handlePreferenceUpdate('dateFormat', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {dateFormats.map((format) => (
                        <SelectItem key={format.value} value={format.value}>
                          {format.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Separator />

              <div>
                <Label htmlFor="theme">Theme</Label>
                <Select value={settings.preferences.theme} onValueChange={(value: 'light' | 'dark' | 'auto') => handlePreferenceUpdate('theme', value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="light">Light</SelectItem>
                    <SelectItem value="dark">Dark</SelectItem>
                    <SelectItem value="auto">Auto (System)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="data" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Data Management</CardTitle>
              <CardDescription>Configure how data is handled and exported</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="refreshInterval">Data Refresh Interval (minutes)</Label>
                  <Select value={settings.dataSettings.refreshInterval.toString()} onValueChange={(value) => handleDataSettingUpdate('refreshInterval', parseInt(value))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="5">5 minutes</SelectItem>
                      <SelectItem value="15">15 minutes</SelectItem>
                      <SelectItem value="30">30 minutes</SelectItem>
                      <SelectItem value="60">1 hour</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="exportFormat">Default Export Format</Label>
                  <Select value={settings.dataSettings.exportFormat} onValueChange={(value) => handleDataSettingUpdate('exportFormat', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {exportFormats.map((format) => (
                        <SelectItem key={format.value} value={format.value}>
                          {format.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="dataRetention">Data Retention (days)</Label>
                  <Input
                    id="dataRetention"
                    type="number"
                    value={settings.dataSettings.dataRetention}
                    onChange={(e) => handleDataSettingUpdate('dataRetention', parseInt(e.target.value))}
                  />
                </div>
                <div>
                  <Label htmlFor="maxDataPoints">Max Data Points</Label>
                  <Input
                    id="maxDataPoints"
                    type="number"
                    value={settings.dataSettings.maxDataPoints}
                    onChange={(e) => handleDataSettingUpdate('maxDataPoints', parseInt(e.target.value))}
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="autoExport"
                  checked={settings.dataSettings.autoExport}
                  onCheckedChange={(checked) => handleDataSettingUpdate('autoExport', checked)}
                />
                <Label htmlFor="autoExport">Enable automatic data export</Label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Security Settings</CardTitle>
              <CardDescription>Manage your account security and authentication</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="sessionTimeout">Session Timeout (minutes)</Label>
                  <Select value={settings.security.sessionTimeout.toString()} onValueChange={(value) => handleSecurityUpdate('sessionTimeout', parseInt(value))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="15">15 minutes</SelectItem>
                      <SelectItem value="30">30 minutes</SelectItem>
                      <SelectItem value="60">1 hour</SelectItem>
                      <SelectItem value="480">8 hours</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="passwordExpiry">Password Expiry (days)</Label>
                  <Select value={settings.security.passwordExpiry.toString()} onValueChange={(value) => handleSecurityUpdate('passwordExpiry', parseInt(value))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="30">30 days</SelectItem>
                      <SelectItem value="60">60 days</SelectItem>
                      <SelectItem value="90">90 days</SelectItem>
                      <SelectItem value="180">180 days</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="twoFactor"
                    checked={settings.security.twoFactorEnabled}
                    onCheckedChange={(checked) => handleSecurityUpdate('twoFactorEnabled', checked)}
                  />
                  <Label htmlFor="twoFactor">Enable Two-Factor Authentication</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="loginNotifications"
                    checked={settings.security.loginNotifications}
                    onCheckedChange={(checked) => handleSecurityUpdate('loginNotifications', checked)}
                  />
                  <Label htmlFor="loginNotifications">Notify on new login attempts</Label>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
              <CardDescription>Choose how and when you want to be notified</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="emailNotifications"
                    checked={settings.preferences.notifications.email}
                    onCheckedChange={(checked) => handleNotificationUpdate('email', checked)}
                  />
                  <Label htmlFor="emailNotifications">Email Notifications</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="pushNotifications"
                    checked={settings.preferences.notifications.push}
                    onCheckedChange={(checked) => handleNotificationUpdate('push', checked)}
                  />
                  <Label htmlFor="pushNotifications">Push Notifications</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="smsNotifications"
                    checked={settings.preferences.notifications.sms}
                    onCheckedChange={(checked) => handleNotificationUpdate('sms', checked)}
                  />
                  <Label htmlFor="smsNotifications">SMS Notifications</Label>
                </div>
              </div>

              <Separator />

              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="marketUpdates"
                    checked={settings.preferences.notifications.marketUpdates}
                    onCheckedChange={(checked) => handleNotificationUpdate('marketUpdates', checked)}
                  />
                  <Label htmlFor="marketUpdates">Market Updates & Trends</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="priceAlerts"
                    checked={settings.preferences.notifications.priceAlerts}
                    onCheckedChange={(checked) => handleNotificationUpdate('priceAlerts', checked)}
                  />
                  <Label htmlFor="priceAlerts">Price Change Alerts</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="reportReady"
                    checked={settings.preferences.notifications.reportReady}
                    onCheckedChange={(checked) => handleNotificationUpdate('reportReady', checked)}
                  />
                  <Label htmlFor="reportReady">Report Generation Complete</Label>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* System Status */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>System Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                <CheckCircle className="h-8 w-8 mx-auto mb-2" />
              </div>
              <p className="text-sm text-gray-600">All Systems Operational</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                <Database className="h-8 w-8 mx-auto mb-2" />
              </div>
              <p className="text-sm text-gray-600">Data Sync Active</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                <Shield className="h-8 w-8 mx-auto mb-2" />
              </div>
              <p className="text-sm text-gray-600">Security Verified</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
