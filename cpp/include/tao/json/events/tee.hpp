// Copyright (c) 2016-2017 Dr. Colin Hirsch and Daniel Frey
// Please see LICENSE for license or visit https://github.com/taocpp/json/

#ifndef TAOCPP_JSON_INCLUDE_EVENTS_TEE_HPP
#define TAOCPP_JSON_INCLUDE_EVENTS_TEE_HPP

#include <cstdint>
#include <string>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>

#include "../internal/integer_sequence.hpp"

namespace tao
{
   namespace json
   {
      namespace internal
      {
         template< typename T >
         struct strip_reference_wrapper
         {
            using type = T;
         };

         template< typename T >
         struct strip_reference_wrapper< std::reference_wrapper< T > >
         {
            using type = T&;
         };

         template< typename T >
         using decay_and_strip_t = typename strip_reference_wrapper< typename std::decay< T >::type >::type;

         template< typename >
         struct events_apply;

         template< std::size_t... Is >
         struct events_apply< index_sequence< Is... > >
         {
            using sink = bool[];

            template< typename... Ts >
            static void null( std::tuple< Ts... >& t )
            {
               (void)sink{ ( std::get< Is >( t ).null(), true )... };
            }

            template< typename... Ts >
            static void boolean( std::tuple< Ts... >& t, const bool v )
            {
               (void)sink{ ( std::get< Is >( t ).boolean( v ), true )... };
            }

            template< typename... Ts >
            static void number( std::tuple< Ts... >& t, const std::int64_t v )
            {
               (void)sink{ ( std::get< Is >( t ).number( v ), true )... };
            }

            template< typename... Ts >
            static void number( std::tuple< Ts... >& t, const std::uint64_t v )
            {
               (void)sink{ ( std::get< Is >( t ).number( v ), true )... };
            }

            template< typename... Ts >
            static void number( std::tuple< Ts... >& t, const double v )
            {
               (void)sink{ ( std::get< Is >( t ).number( v ), true )... };
            }

            template< typename... Ts >
            static void string( std::tuple< Ts... >& t, const std::string& v )
            {
               (void)sink{ ( std::get< Is >( t ).string( v ), true )... };
            }

            template< typename... Ts >
            static void binary( std::tuple< Ts... >& t, const std::vector< byte >& v )
            {
               (void)sink{ ( std::get< Is >( t ).binary( v ), true )... };
            }

            template< typename... Ts >
            static void begin_array( std::tuple< Ts... >& t )
            {
               (void)sink{ ( std::get< Is >( t ).begin_array(), true )... };
            }

            template< typename... Ts >
            static void begin_array( std::tuple< Ts... >& t, const std::size_t size )
            {
               (void)sink{ ( std::get< Is >( t ).begin_array( size ), true )... };
            }

            template< typename... Ts >
            static void element( std::tuple< Ts... >& t )
            {
               (void)sink{ ( std::get< Is >( t ).element(), true )... };
            }

            template< typename... Ts >
            static void end_array( std::tuple< Ts... >& t )
            {
               (void)sink{ ( std::get< Is >( t ).end_array(), true )... };
            }

            template< typename... Ts >
            static void end_array( std::tuple< Ts... >& t, const std::size_t size )
            {
               (void)sink{ ( std::get< Is >( t ).end_array( size ), true )... };
            }

            template< typename... Ts >
            static void begin_object( std::tuple< Ts... >& t )
            {
               (void)sink{ ( std::get< Is >( t ).begin_object(), true )... };
            }

            template< typename... Ts >
            static void begin_object( std::tuple< Ts... >& t, const std::size_t size )
            {
               (void)sink{ ( std::get< Is >( t ).begin_object( size ), true )... };
            }

            template< typename... Ts >
            static void key( std::tuple< Ts... >& t, const std::string& v )
            {
               (void)sink{ ( std::get< Is >( t ).key( v ), true )... };
            }

            template< typename... Ts >
            static void member( std::tuple< Ts... >& t )
            {
               (void)sink{ ( std::get< Is >( t ).member(), true )... };
            }

            template< typename... Ts >
            static void end_object( std::tuple< Ts... >& t )
            {
               (void)sink{ ( std::get< Is >( t ).end_object(), true )... };
            }

            template< typename... Ts >
            static void end_object( std::tuple< Ts... >& t, const std::size_t size )
            {
               (void)sink{ ( std::get< Is >( t ).end_object( size ), true )... };
            }
         };

      }  // namespace internal

      namespace events
      {
         // Events consumer that forwards to two nested consumers.

         template< typename... Ts >
         class tee
         {
         private:
            static_assert( sizeof...( Ts ) >= 1, "tao::json::events::tee requires at least one consumer" );

            static constexpr std::size_t S = sizeof...( Ts );

            using I = internal::make_index_sequence< S >;
            using H = internal::make_index_sequence< S - 1 >;

            std::tuple< Ts... > ts;

         public:
            template< typename... Us >
            tee( Us&&... us )
               : ts( std::forward< Us >( us )... )
            {
            }

            void null()
            {
               internal::events_apply< I >::null( ts );
            }

            void boolean( const bool v )
            {
               internal::events_apply< I >::boolean( ts, v );
            }

            void number( const std::int64_t v )
            {
               internal::events_apply< I >::number( ts, v );
            }

            void number( const std::uint64_t v )
            {
               internal::events_apply< I >::number( ts, v );
            }

            void number( const double v )
            {
               internal::events_apply< I >::number( ts, v );
            }

            void string( const std::string& v )
            {
               internal::events_apply< I >::string( ts, v );
            }

            void string( std::string&& v )
            {
               internal::events_apply< H >::string( ts, v );
               std::get< S - 1 >( ts ).string( std::move( v ) );
            }

            void binary( const std::vector< byte >& v )
            {
               internal::events_apply< I >::binary( ts, v );
            }

            void binary( std::vector< byte >&& v )
            {
               internal::events_apply< H >::binary( ts, v );
               std::get< S - 1 >( ts ).binary( std::move( v ) );
            }

            void begin_array()
            {
               internal::events_apply< I >::begin_array( ts );
            }

            void begin_array( const std::size_t size )
            {
               internal::events_apply< I >::begin_array( ts, size );
            }

            void element()
            {
               internal::events_apply< I >::element( ts );
            }

            void end_array()
            {
               internal::events_apply< I >::end_array( ts );
            }

            void end_array( const std::size_t size )
            {
               internal::events_apply< I >::end_array( ts, size );
            }

            void begin_object()
            {
               internal::events_apply< I >::begin_object( ts );
            }

            void begin_object( const std::size_t size )
            {
               internal::events_apply< I >::begin_object( ts, size );
            }

            void key( const std::string& v )
            {
               internal::events_apply< I >::key( ts, v );
            }

            void key( std::string&& v )
            {
               internal::events_apply< H >::key( ts, v );
               std::get< S - 1 >( ts ).key( std::move( v ) );
            }

            void member()
            {
               internal::events_apply< I >::member( ts );
            }

            void end_object()
            {
               internal::events_apply< I >::end_object( ts );
            }

            void end_object( const std::size_t size )
            {
               internal::events_apply< I >::end_object( ts, size );
            }
         };

         template< typename... T >
         tee< internal::decay_and_strip_t< T >... > make_tee( T&&... t )
         {
            return tee< internal::decay_and_strip_t< T >... >( std::forward< T >( t )... );
         }

         template< typename... T >
         tee< T&... > tie( T&... t )
         {
            return tee< T&... >( t... );
         }

      }  // namespace events

   }  // namespace json

}  // namespace tao

#endif
