export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  graphql_public: {
    Tables: {
      [_ in never]: never
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      graphql: {
        Args: {
          operationName?: string
          query?: string
          variables?: Json
          extensions?: Json
        }
        Returns: Json
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
  public: {
    Tables: {
      approved_emails: {
        Row: {
          added_by: string | null
          created_at: string | null
          email: string
          id: string
          notes: string | null
        }
        Insert: {
          added_by?: string | null
          created_at?: string | null
          email: string
          id?: string
          notes?: string | null
        }
        Update: {
          added_by?: string | null
          created_at?: string | null
          email?: string
          id?: string
          notes?: string | null
        }
        Relationships: []
      }
      audit: {
        Row: {
          audit_id: string
          brand_id: string | null
          created_timestamp: string
          product_id: string | null
          status: string
          user_id: string
        }
        Insert: {
          audit_id?: string
          brand_id?: string | null
          created_timestamp?: string
          product_id?: string | null
          status: string
          user_id: string
        }
        Update: {
          audit_id?: string
          brand_id?: string | null
          created_timestamp?: string
          product_id?: string | null
          status?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "audit_brand_id_fkey"
            columns: ["brand_id"]
            isOneToOne: false
            referencedRelation: "brand"
            referencedColumns: ["brand_id"]
          },
          {
            foreignKeyName: "audit_product_id_fkey"
            columns: ["product_id"]
            isOneToOne: false
            referencedRelation: "product"
            referencedColumns: ["product_id"]
          },
          {
            foreignKeyName: "audit_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["user_id"]
          },
        ]
      }
      brand: {
        Row: {
          brand_description: string | null
          brand_id: string
          brand_name: string
          domain: string | null
        }
        Insert: {
          brand_description?: string | null
          brand_id?: string
          brand_name: string
          domain?: string | null
        }
        Update: {
          brand_description?: string | null
          brand_id?: string
          brand_name?: string
          domain?: string | null
        }
        Relationships: []
      }
      meeting_requests: {
        Row: {
          company: string
          created_at: string
          email: string
          full_name: string
          id: string
          message: string | null
        }
        Insert: {
          company: string
          created_at?: string
          email: string
          full_name: string
          id?: string
          message?: string | null
        }
        Update: {
          company?: string
          created_at?: string
          email?: string
          full_name?: string
          id?: string
          message?: string | null
        }
        Relationships: []
      }
      personas: {
        Row: {
          audit_id: string | null
          brand_id: string | null
          persona_characteristics: string | null
          persona_description: string | null
          persona_id: string
          persona_type: string
          product_id: string | null
        }
        Insert: {
          audit_id?: string | null
          brand_id?: string | null
          persona_characteristics?: string | null
          persona_description?: string | null
          persona_id?: string
          persona_type: string
          product_id?: string | null
        }
        Update: {
          audit_id?: string | null
          brand_id?: string | null
          persona_characteristics?: string | null
          persona_description?: string | null
          persona_id?: string
          persona_type?: string
          product_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "personas_audit_id_fkey"
            columns: ["audit_id"]
            isOneToOne: false
            referencedRelation: "audit"
            referencedColumns: ["audit_id"]
          },
          {
            foreignKeyName: "personas_brand_id_fkey"
            columns: ["brand_id"]
            isOneToOne: false
            referencedRelation: "brand"
            referencedColumns: ["brand_id"]
          },
          {
            foreignKeyName: "personas_product_id_fkey"
            columns: ["product_id"]
            isOneToOne: false
            referencedRelation: "product"
            referencedColumns: ["product_id"]
          },
        ]
      }
      products: {
        Row: {
          brand_id: string | null
          created_at: string
          id: string
          name: string
          value_props: string[] | null
        }
        Insert: {
          brand_id?: string | null
          created_at?: string
          id?: string
          name: string
          value_props?: string[] | null
        }
        Update: {
          brand_id?: string | null
          created_at?: string
          id?: string
          name?: string
          value_props?: string[] | null
        }
        Relationships: [
          {
            foreignKeyName: "products_brand_id_fkey"
            columns: ["brand_id"]
            isOneToOne: false
            referencedRelation: "brand"
            referencedColumns: ["brand_id"]
          },
        ]
      }
      profiles: {
        Row: {
          avatar_url: string | null
          full_name: string | null
          updated_at: string | null
          user_id: string
          username: string | null
        }
        Insert: {
          avatar_url?: string | null
          full_name?: string | null
          updated_at?: string | null
          user_id: string
          username?: string | null
        }
        Update: {
          avatar_url?: string | null
          full_name?: string | null
          updated_at?: string | null
          user_id?: string
          username?: string | null
        }
        Relationships: []
      }
      queries: {
        Row: {
          audit_id: string
          persona: string
          query_id: string
          query_text: string
          query_type: string | null
          topic_name: string | null
          topic_type: string | null
        }
        Insert: {
          audit_id: string
          persona: string
          query_id?: string
          query_text: string
          query_type?: string | null
          topic_name?: string | null
          topic_type?: string | null
        }
        Update: {
          audit_id?: string
          persona?: string
          query_id?: string
          query_text?: string
          query_type?: string | null
          topic_name?: string | null
          topic_type?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "queries_audit_id_fkey"
            columns: ["audit_id"]
            isOneToOne: false
            referencedRelation: "audit"
            referencedColumns: ["audit_id"]
          },
        ]
      }
      recommendations: {
        Row: {
          audit_id: string
          category: string | null
          recommendation_id: string
          text: string
        }
        Insert: {
          audit_id: string
          category?: string | null
          recommendation_id?: string
          text: string
        }
        Update: {
          audit_id?: string
          category?: string | null
          recommendation_id?: string
          text?: string
        }
        Relationships: [
          {
            foreignKeyName: "recommendations_audit_id_fkey"
            columns: ["audit_id"]
            isOneToOne: false
            referencedRelation: "audit"
            referencedColumns: ["audit_id"]
          },
        ]
      }
      responses: {
        Row: {
          model: string
          query_id: string
          response_id: string
          response_text: string
        }
        Insert: {
          model: string
          query_id: string
          response_id?: string
          response_text: string
        }
        Update: {
          model?: string
          query_id?: string
          response_id?: string
          response_text?: string
        }
        Relationships: [
          {
            foreignKeyName: "responses_query_id_fkey"
            columns: ["query_id"]
            isOneToOne: false
            referencedRelation: "queries"
            referencedColumns: ["query_id"]
          },
        ]
      }
      score_breakdown: {
        Row: {
          audit_id: string
          brand_mentions: Json | null
          score_id: string
          value: number
        }
        Insert: {
          audit_id: string
          brand_mentions?: Json | null
          score_id?: string
          value: number
        }
        Update: {
          audit_id?: string
          brand_mentions?: Json | null
          score_id?: string
          value?: number
        }
        Relationships: [
          {
            foreignKeyName: "score_breakdown_audit_id_fkey"
            columns: ["audit_id"]
            isOneToOne: false
            referencedRelation: "audit"
            referencedColumns: ["audit_id"]
          },
        ]
      }
      Test_Table: {
        Row: {
          "Brand name": string | null
          created_at: string
          id: number
        }
        Insert: {
          "Brand name"?: string | null
          created_at?: string
          id?: number
        }
        Update: {
          "Brand name"?: string | null
          created_at?: string
          id?: number
        }
        Relationships: []
      }
      topics: {
        Row: {
          audit_id: string
          topic_id: string
          topic_name: string
          topic_type: string | null
          topic_category: 'unbranded' | 'branded' | 'comparative'
          visibility: number | null
        }
        Insert: {
          audit_id: string
          topic_id?: string
          topic_name: string
          topic_type?: string | null
          topic_category: 'unbranded' | 'branded' | 'comparative'
          visibility?: number | null
        }
        Update: {
          audit_id?: string
          topic_id?: string
          topic_name?: string
          topic_type?: string | null
          topic_category?: 'unbranded' | 'branded' | 'comparative'
          visibility?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "topics_audit_id_fkey"
            columns: ["audit_id"]
            isOneToOne: false
            referencedRelation: "audit"
            referencedColumns: ["audit_id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DefaultSchema = Database[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof Database },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof Database },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends { schema: keyof Database }
  ? Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  graphql_public: {
    Enums: {},
  },
  public: {
    Enums: {},
  },
} as const
