import { docs } from '@/.source';
import * as LucideIcons from 'lucide-react';
import React from 'react';
import { loader } from 'fumadocs-core/source';

// See https://fumadocs.vercel.app/docs/headless/source-api for more info
export const source = loader({
  baseUrl: '/docs',
  source: docs.toFumadocsSource(),
  icon(iconName?: string) {
    if (!iconName) return;
    const IconComponent = LucideIcons[iconName as keyof typeof LucideIcons];
    if (!IconComponent) return;
    // Cast to ElementType to satisfy React.createElement overload
    const Component = IconComponent as React.ElementType;
    return React.createElement(Component);
  },
});
