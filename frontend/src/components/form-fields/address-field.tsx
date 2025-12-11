"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { FormField } from "@/types";

interface AddressFieldProps {
  field: FormField;
  value: AddressValue;
  onChange: (value: AddressValue) => void;
}

export interface AddressValue {
  street?: string;
  street2?: string;
  city?: string;
  state?: string;
  zip?: string;
  country?: string;
}

const US_STATES = [
  'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
  'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
  'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan',
  'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
  'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio',
  'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
  'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia',
  'Wisconsin', 'Wyoming'
];

const COUNTRIES = [
  'United States', 'Canada', 'United Kingdom', 'Australia', 'Germany', 'France',
  'Spain', 'Italy', 'Netherlands', 'Sweden', 'Norway', 'Denmark', 'Finland',
  'Switzerland', 'Austria', 'Belgium', 'Ireland', 'Portugal', 'New Zealand',
  'Japan', 'South Korea', 'Singapore', 'India', 'Brazil', 'Mexico'
];

export function AddressField({ field, value, onChange }: AddressFieldProps) {
  const includeCountry = field.includeCountry !== false;
  const includeZip = field.includeZip !== false;

  const updateField = (key: keyof AddressValue, val: string) => {
    onChange({ ...value, [key]: val });
  };

  return (
    <div className="space-y-3">
      <Label>
        {field.label}
        {field.required && <span className="text-red-500 ml-1">*</span>}
      </Label>
      
      <div className="space-y-3">
        <div>
          <Label htmlFor={`${field.id}-street`} className="text-xs text-muted-foreground">
            Street Address
          </Label>
          <Input
            id={`${field.id}-street`}
            placeholder="123 Main Street"
            value={value?.street || ''}
            onChange={(e) => updateField('street', e.target.value)}
          />
        </div>
        
        <div>
          <Label htmlFor={`${field.id}-street2`} className="text-xs text-muted-foreground">
            Apt, Suite, etc. (optional)
          </Label>
          <Input
            id={`${field.id}-street2`}
            placeholder="Apt 4B"
            value={value?.street2 || ''}
            onChange={(e) => updateField('street2', e.target.value)}
          />
        </div>
        
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label htmlFor={`${field.id}-city`} className="text-xs text-muted-foreground">
              City
            </Label>
            <Input
              id={`${field.id}-city`}
              placeholder="New York"
              value={value?.city || ''}
              onChange={(e) => updateField('city', e.target.value)}
            />
          </div>
          
          <div>
            <Label htmlFor={`${field.id}-state`} className="text-xs text-muted-foreground">
              State / Province
            </Label>
            <Select
              value={value?.state || ''}
              onValueChange={(val) => updateField('state', val)}
            >
              <SelectTrigger id={`${field.id}-state`}>
                <SelectValue placeholder="Select state" />
              </SelectTrigger>
              <SelectContent>
                {US_STATES.map((state) => (
                  <SelectItem key={state} value={state}>
                    {state}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-3">
          {includeZip && (
            <div>
              <Label htmlFor={`${field.id}-zip`} className="text-xs text-muted-foreground">
                ZIP / Postal Code
              </Label>
              <Input
                id={`${field.id}-zip`}
                placeholder="10001"
                value={value?.zip || ''}
                onChange={(e) => updateField('zip', e.target.value)}
              />
            </div>
          )}
          
          {includeCountry && (
            <div>
              <Label htmlFor={`${field.id}-country`} className="text-xs text-muted-foreground">
                Country
              </Label>
              <Select
                value={value?.country || 'United States'}
                onValueChange={(val) => updateField('country', val)}
              >
                <SelectTrigger id={`${field.id}-country`}>
                  <SelectValue placeholder="Select country" />
                </SelectTrigger>
                <SelectContent>
                  {COUNTRIES.map((country) => (
                    <SelectItem key={country} value={country}>
                      {country}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </div>
      </div>
      
      {field.help && (
        <p className="text-xs text-muted-foreground">{field.help}</p>
      )}
    </div>
  );
}
