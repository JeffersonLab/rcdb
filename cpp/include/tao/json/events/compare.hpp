// Copyright (c) 2016-2017 Dr. Colin Hirsch and Daniel Frey
// Please see LICENSE for license or visit https://github.com/taocpp/json/

#ifndef TAOCPP_JSON_INCLUDE_EVENTS_COMPARE_HPP
#define TAOCPP_JSON_INCLUDE_EVENTS_COMPARE_HPP

#include "../value.hpp"

#include <cstddef>
#include <cstdint>
#include <set>
#include <string>
#include <vector>

namespace tao
{
   namespace json
   {
      namespace internal
      {
         template< template< typename... > class Traits >
         class events_compare
         {
         protected:
            using value_t = basic_value< Traits >;

            std::vector< const value_t* > m_current;
            std::vector< std::size_t > m_array_index;
            // TODO: use std::unordered_set? or even std::vector!?
            std::vector< std::set< const value_t* > > m_object_keys;
            bool m_match = true;

         public:
            events_compare() = default;

            events_compare( const events_compare& ) = delete;
            events_compare( events_compare&& ) = delete;

            void operator=( const events_compare& ) = delete;
            void operator=( events_compare&& ) = delete;

            void reset() noexcept
            {
               m_current.clear();
               m_array_index.clear();
               m_object_keys.clear();
               m_match = true;
            }

            static const value_t* skip_pointer( const value_t* p ) noexcept
            {
               while( p && p->is_raw_ptr() ) {
                  p = p->unsafe_get_raw_ptr();
               }
               return p;
            }

            void push( const value_t* p )
            {
               m_current.push_back( skip_pointer( p ) );
            }

            bool match() const noexcept
            {
               return m_match;
            }

            const value_t& current() const noexcept
            {
               return *m_current.back();
            }

            void null() noexcept
            {
               m_match = m_match && ( m_current.back() != nullptr ) && ( current().is_null() );
            }

            void boolean( const bool v ) noexcept
            {
               m_match = m_match && ( m_current.back() != nullptr ) && ( current() == v );
            }

            void number( const std::int64_t v ) noexcept
            {
               m_match = m_match && ( m_current.back() != nullptr ) && ( current() == v );
            }

            void number( const std::uint64_t v ) noexcept
            {
               m_match = m_match && ( m_current.back() != nullptr ) && ( current() == v );
            }

            void number( const double v ) noexcept
            {
               m_match = m_match && ( m_current.back() != nullptr ) && ( current() == v );
            }

            void string( const std::string& v ) noexcept
            {
               m_match = m_match && ( m_current.back() != nullptr ) && ( current() == v );
            }

            void binary( const std::vector< byte >& v ) noexcept
            {
               m_match = m_match && ( m_current.back() != nullptr ) && ( current() == v );
            }

            void begin_array( const std::size_t = 0 )
            {
               if( m_current.back() == nullptr ) {
                  m_match = false;
                  m_current.push_back( nullptr );
               }
               else {
                  const auto& a = current();
                  if( !a.is_array() ) {
                     m_match = false;
                     m_current.push_back( nullptr );
                  }
                  else if( !a.unsafe_get_array().empty() ) {
                     push( &a.unsafe_get_array().front() );
                  }
                  else {
                     m_current.push_back( nullptr );
                  }
               }
               m_array_index.push_back( 0 );
            }

            void element() noexcept
            {
               const auto i = ++m_array_index.back();
               if( m_match ) {
                  if( m_current.back() != nullptr ) {
                     const auto& a = ( *( m_current.end() - 2 ) )->unsafe_get_array();
                     if( i < a.size() ) {
                        m_current.back() = skip_pointer( &a[ i ] );
                     }
                     else {
                        m_current.back() = nullptr;
                     }
                  }
               }
            }

            void end_array( const std::size_t = 0 ) noexcept
            {
               m_current.pop_back();
               if( m_match ) {
                  if( m_array_index.back() != current().unsafe_get_array().size() ) {
                     m_match = false;
                  }
               }
               m_array_index.pop_back();
            }

            void begin_object( const std::size_t = 0 )
            {
               if( m_current.back() == nullptr ) {
                  m_match = false;
               }
               else {
                  const auto& o = current();
                  if( !o.is_object() ) {
                     m_match = false;
                  }
               }
               m_object_keys.emplace_back();
            }

            void key( const std::string& v )
            {
               if( !m_match ) {
                  m_current.push_back( nullptr );
               }
               else if( const auto* p = current().unsafe_find( v ) ) {
                  if( !m_object_keys.back().insert( p ).second ) {
                     m_match = false;  // duplicate key found! -> fail
                     m_current.push_back( nullptr );
                  }
                  else {
                     push( p );
                  }
               }
               else {
                  m_match = false;
                  m_current.push_back( nullptr );
               }
            }

            void member() noexcept
            {
               m_current.pop_back();
            }

            void end_object( const std::size_t = 0 ) noexcept
            {
               if( m_match ) {
                  if( m_object_keys.back().size() != current().unsafe_get_object().size() ) {
                     m_match = false;
                  }
               }
               m_object_keys.pop_back();
            }
         };

      }  // namespace internal

      namespace events
      {
         // Events consumer that compares against a JSON Value.

         template< template< typename... > class Traits >
         class basic_compare : public internal::events_compare< Traits >
         {
         private:
            using typename internal::events_compare< Traits >::value_t;
            const value_t m_value;

         public:
            explicit basic_compare( const value_t& v )
               : m_value( v )
            {
               reset();
            }

            explicit basic_compare( value_t&& v )
               : m_value( std::move( v ) )
            {
               reset();
            }

            basic_compare( const basic_compare& ) = delete;
            basic_compare( basic_compare&& ) = delete;

            void operator=( const basic_compare& ) = delete;
            void operator=( basic_compare&& ) = delete;

            void reset()
            {
               internal::events_compare< Traits >::reset();
               internal::events_compare< Traits >::push( &m_value );
            }
         };

         using compare = basic_compare< traits >;

      }  // namespace events

   }  // namespace json

}  // namespace tao

#endif
